from functools import wraps
from flask import redirect, url_for, flash, session, jsonify
import sqlite3

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
            cursor.execute('SELECT rol FROM Usuario WHERE nombre_usuario = ?', (session['usuario'],))
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
            cursor.execute('SELECT rol FROM Usuario WHERE nombre_usuario = ?', (session['usuario'],))
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
    return require_api_role('trabajador')(f)
