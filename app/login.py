from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, login_required
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.models import Usuario
from app.session_decorators import nocache

login_blueprint = Blueprint('login', __name__)

# Crear tabla Usuario si no existe
def crear_tabla_usuario():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Usuario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre_completo TEXT NOT NULL,
            nombre_usuario TEXT NOT NULL UNIQUE,
            documento TEXT NOT NULL UNIQUE,
            correo TEXT NOT NULL UNIQUE,
            contraseña TEXT NOT NULL,
            rol TEXT DEFAULT 'trabajador',
            estado TEXT DEFAULT 'activo',
            grupo TEXT
        )
    ''')

    conn.commit()
    conn.close()


# Conexión a la base de datos
def get_db_connection():
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    return conn

# Ruta del login
@login_blueprint.route('/login', methods=['GET', 'POST'])
@nocache
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contrasena = request.form['contrasena']

        # Buscar usuario usando el modelo
        usuario = Usuario.get_by_username(nombre_usuario)
        
        # Verificar si el usuario existe, está activo y la contraseña es correcta
        if usuario is None:
            flash('El usuario es incorrecto.')
        elif usuario.estado != 'activo':
            flash('El usuario está inactivo. Contacta al administrador.')
        elif not check_password_hash(usuario.contraseña, contrasena):
            flash('Contraseña incorrecta.')
        else:
            # Iniciar sesión con Flask-Login
            login_user(usuario)
            
            # Mantener información en sesión para compatibilidad con código existente
            session['usuario'] = {
                'id': usuario.id,
                'email': usuario.correo,
                'nombre_usuario': usuario.nombre_usuario
            }
            session['usuario_id'] = usuario.id
            session['grupo'] = usuario.grupo
            session['rol'] = usuario.rol  # <-- Asegura que el rol esté en la sesión
            
            # Redirigir según el rol
            if usuario.rol == 'admin':
                return redirect(url_for('administrador'))
            elif usuario.rol == 'lider':
                return redirect(url_for('lider.lideres'))
            else:
                return redirect(url_for('trabajador.trabajador'))

    return render_template('login.html')


# Ruta del registro
@login_blueprint.route('/crear_usuario', methods=['GET', 'POST'])
@nocache
def crear_usuario():
    if request.method == 'POST':
        nombre = request.form['nombre']
        nombre_usuario = request.form['nombre_usuario']
        documento = request.form['documento']
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        # El grupo se asigna después del registro, no durante el proceso de creación

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                nombre,
                nombre_usuario,
                documento,
                correo,
                generate_password_hash(contrasena)  # Encriptación
            ))
            conn.commit()
            flash('Usuario creado exitosamente.')
            return redirect(url_for('login.login'))
        except sqlite3.IntegrityError:
            flash('El nombre de usuario, documento o correo ya existe.')
        finally:
            conn.close()

    return render_template('crear_usuario.html')
