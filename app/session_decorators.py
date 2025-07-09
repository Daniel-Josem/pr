
from functools import wraps
from flask import redirect, url_for, flash, session, jsonify, make_response
import sqlite3

def nocache(f):
    """
    Decorador que previene el caché del navegador
    Útil para páginas con información sensible o que cambian frecuentemente
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = make_response(f(*args, **kwargs))
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    return decorated_function

def require_login(f):
    """
    Decorador simple que requiere que el usuario esté logueado
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session:
            flash('Debes iniciar sesión para acceder a esta página.', 'warning')
            return redirect(url_for('login.login'))
        return f(*args, **kwargs)
    return decorated_function

def require_role(role):
    """
    Decorador que requiere un rol específico
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si está logueado
            if 'usuario' not in session:
                flash('Debes iniciar sesión para acceder a esta página.', 'warning')
                return redirect(url_for('login.login'))
            
            # Verificar el rol
            conn = sqlite3.connect('gestor_de_tareas.db')
            cursor = conn.cursor()
            usuario = session.get('usuario')
            if isinstance(usuario, dict):
                nombre_usuario = usuario.get('nombre_usuario')
            else:
                nombre_usuario = usuario
            cursor.execute('SELECT rol FROM Usuario WHERE nombre_usuario = ?', (nombre_usuario,))
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                flash('Usuario no válido', 'error')
                session.clear()
                return redirect(url_for('login.login'))
            
            if resultado[0] != role:
                flash(f'No tienes permisos de {role} para acceder a esta página.', 'error')
                return redirect(url_for('login.login'))
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_api_role(role):
    """
    Decorador que requiere un rol específico para APIs (retorna JSON)
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si está logueado
            if 'usuario' not in session:
                return jsonify({'error': 'No autenticado'}), 401
            
            # Verificar el rol
            conn = sqlite3.connect('gestor_de_tareas.db')
            cursor = conn.cursor()
            usuario = session.get('usuario')
            if isinstance(usuario, dict):
                nombre_usuario = usuario.get('nombre_usuario')
            else:
                nombre_usuario = usuario
            cursor.execute('SELECT rol FROM Usuario WHERE nombre_usuario = ?', (nombre_usuario,))
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                return jsonify({'error': 'Usuario no válido'}), 401
            
            if resultado[0] != role:
                return jsonify({'error': f'No tienes permisos de {role}'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def admin_required(f):
    """Decorador específico para administradores"""
    return require_role('admin')(f)

def lider_required(f):
    """Decorador específico para líderes"""
    return require_role('lider')(f)

def trabajador_required(f):
    """Decorador específico para trabajadores"""
    return require_role('trabajador')(f)

def api_admin_required(f):
    """Decorador específico para APIs de administradores"""
    return require_api_role('admin')(f)

def api_lider_required(f):
    """Decorador específico para APIs de líderes"""
    return require_api_role('lider')(f)

def api_trabajador_required(f):
    """Decorador específico para APIs de trabajadores"""

# Versión única: Decorador para APIs de trabajador que siempre responde JSON en caso de error
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'trabajador':
            return jsonify({'error': 'Acceso no autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function

def secure_route(allowed_roles=None):
    """
    Decorador más robusto que combina validación de sesión, rol y nocache
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si hay sesión activa
            if 'usuario' not in session or 'usuario_id' not in session:
                session.clear()  # Limpiar cualquier dato residual
                flash('Tu sesión ha expirado. Por favor, inicia sesión nuevamente.', 'warning')
                return redirect(url_for('login.login'))
            
            # Verificar que el usuario existe y está activo en la BD
            conn = sqlite3.connect('gestor_de_tareas.db')
            cursor = conn.cursor()
            usuario_id = session.get('usuario_id')
            
            cursor.execute('SELECT rol, estado FROM Usuario WHERE id = ?', (usuario_id,))
            resultado = cursor.fetchone()
            conn.close()
            
            if not resultado:
                session.clear()
                flash('Usuario no válido. Por favor, inicia sesión nuevamente.', 'error')
                return redirect(url_for('login.login'))
            
            rol_usuario, estado_usuario = resultado
            
            # Verificar que el usuario está activo
            if estado_usuario != 'activo':
                session.clear()
                flash('Tu cuenta está inactiva. Contacta al administrador.', 'error')
                return redirect(url_for('login.login'))
            
            # Verificar roles si se especificaron
            if allowed_roles and rol_usuario not in allowed_roles:
                flash(f'No tienes permisos para acceder a esta página.', 'error')
                return redirect(url_for('login.login'))
            
            # Ejecutar la función con nocache
            response = make_response(f(*args, **kwargs))
            response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
            response.headers['Pragma'] = 'no-cache'
            response.headers['Expires'] = '0'
            return response
        return decorated_function
    return decorator

def api_trabajador_required(f):
    """Decorador específico para APIs de trabajadores"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario' not in session or session.get('rol') != 'trabajador':
            return jsonify({'error': 'Acceso no autorizado'}), 401
        return f(*args, **kwargs)
    return decorated_function