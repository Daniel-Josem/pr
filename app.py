from flask import Flask, render_template, session, redirect, url_for, jsonify, request, current_app, flash
from flask_login import LoginManager, login_required, current_user, logout_user
import sqlite3
import os
from werkzeug.utils import secure_filename
from app.login import login_blueprint
from app.admin import api_blueprint
from app.lider import lider
from app.trabajador import trabajador_blueprint
from app.recuperar import recuperar_bp
from app.models import Usuario
from app.session_decorators import admin_required
from error_handlers import register_error_handlers, register_monitoring_routes, register_security_middleware, setup_rate_limiting
import re
from urllib.parse import unquote
from dotenv import load_dotenv



# Cargar variables de entorno desde .env (soporta renombrar env → .env)
import pathlib
dotenv_path = pathlib.Path('.env')
if not dotenv_path.exists():
    alt_env = pathlib.Path('env')
    if alt_env.exists():
        alt_env.rename('.env')
        print('Archivo env renombrado a .env')
load_dotenv(dotenv_path='.env')

app = Flask(__name__)
# Usar una clave secreta desde variables de entorno o una por defecto
app.secret_key = os.getenv('SECRET_KEY', 'clave_secreta_segura')

# Configurar Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login.login'
login_manager.login_message = 'Por favor, inicia sesión para acceder a esta página.'
login_manager.login_message_category = 'info'


@app.before_request
def clean_malformed_urls():
    """Limpia URLs malformadas antes de procesarlas"""
    try:
        # Decodificar la URL
        decoded_path = unquote(request.path)
        
        # Verificar si contiene caracteres especiales o espacios
        if re.search(r'[^\w\-\._~:/?#\[\]@!$&\'()*+,;=]', decoded_path):
            # Si la URL contiene caracteres especiales, redirigir al inicio
            return redirect(url_for('landing'))
    except Exception:
        # Si hay error decodificando, redirigir al inicio
        return redirect(url_for('landing'))

@login_manager.user_loader
def load_user(user_id):
    print(f"Loading user with ID: {user_id}")  # Debug
    usuario = Usuario.get(user_id)
    print(f"User loaded: {usuario}")  # Debug
    return usuario

# Registrar los Blueprints
app.register_blueprint(login_blueprint)
app.register_blueprint(api_blueprint)
app.register_blueprint(lider)
app.register_blueprint(trabajador_blueprint)
app.register_blueprint(recuperar_bp)

@app.route('/api/tarea/<int:tarea_id>/archivos', methods=['GET'])
def obtener_archivos_tarea(tarea_id):
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT ta.nombre_archivo, ta.ruta_archivo, ta.fecha_subida, u.nombre_completo AS nombre_usuario
        FROM tarea_archivos ta
        JOIN Usuario u ON ta.usuario_id = u.id
        WHERE ta.tarea_id = ?
        ORDER BY ta.fecha_subida DESC
    ''', (tarea_id,))

    archivos = cursor.fetchall()
    conn.close()

    return jsonify([dict(row) for row in archivos])

# Crear tablas y agregar columna 'grupo' si no existe
def crear_tabla_usuario():
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Crear la tabla Usuario sin la columna grupo
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Usuario (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre_completo TEXT NOT NULL,
        nombre_usuario TEXT NOT NULL UNIQUE,
        documento TEXT NOT NULL UNIQUE,
        correo TEXT NOT NULL UNIQUE,
        contraseña TEXT NOT NULL,
        rol TEXT DEFAULT 'trabajador',
        estado TEXT DEFAULT 'activo'
    )''')

    # Verificar si la columna 'grupo' ya existe
    cursor.execute("PRAGMA table_info(Usuario);")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if 'grupo' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN grupo TEXT')
        print("Columna 'grupo' agregada a la tabla Usuario.")
        
    if 'proyecto' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN proyecto TEXT')
        print("Columna 'proyecto' agregada a la tabla Usuario.")

    if 'telefono' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN telefono TEXT')
        print("Columna 'telefono' agregada a la tabla Usuario.")
    
    if 'direccion' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN direccion TEXT')
        print("Columna 'direccion' agregada a la tabla Usuario.")

    # Verificar si la columna 'descripcion' ya existe
    cursor.execute("PRAGMA table_info(Usuario);")
    columnas = [columna[1] for columna in cursor.fetchall()]
    if 'descripcion' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN descripcion TEXT')
        print("Columna 'descripcion' agregada a la tabla Usuario.")

    # Verificar si la columna 'foto' ya existe
    cursor.execute("PRAGMA table_info(Usuario);")
    columnas = [columna[1] for columna in cursor.fetchall()]
    if 'foto' not in columnas:
        cursor.execute('ALTER TABLE Usuario ADD COLUMN foto TEXT')
        print("Columna 'foto' agregada a la tabla Usuario.")

  
# Crear tabla proyectos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Proyecto (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT NOT NULL UNIQUE,
        descripcion TEXT,
        grupo TEXT NOT NULL,
        estado TEXT DEFAULT 'activo',
        fecha_inicio TEXT,
        fecha_fin TEXT
    );
    ''')

    # Crear tabla tareas
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tareas (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      titulo TEXT NOT NULL,
      descripcion TEXT,
      fecha_vencimiento DATE,
      prioridad TEXT,
      estado TEXT DEFAULT 'pendiente',
      id_proyecto INTEGER,
      id_usuario_asignado INTEGER,
      ruta_archivo TEXT,
      curso_destino TEXT,
      FOREIGN KEY(id_usuario_asignado) REFERENCES Usuario(id) ON DELETE SET NULL
    );''')
  # Verificar si la columna 'fecha_registro' ya existe en la tabla tareas
    cursor.execute("PRAGMA table_info(tareas);")
    columnas = [columna[1] for columna in cursor.fetchall()]

    if 'fecha_registro' not in columnas:
        cursor.execute("ALTER TABLE tareas ADD COLUMN fecha_registro DATE")
        cursor.execute("UPDATE tareas SET fecha_registro = DATE('now') WHERE fecha_registro IS NULL")
        print("Columna 'fecha_registro' agregada a la tabla tareas.")


    # Crear tabla mensajes
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS mensajes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    emisor_id INTEGER,
    emisor TEXT,
    receptor_id INTEGER,
    mensaje TEXT,
    tipo TEXT DEFAULT 'texto', 
    sticker TEXT, 
    imagen_url TEXT, 
    audio_url TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );''')

    # Crear tabla notificaciones
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS notificaciones (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      mensaje TEXT NOT NULL,
      leido INTEGER DEFAULT 0,
      fecha DATETIME DEFAULT CURRENT_TIMESTAMP,
      id_usuario INTEGER,
      FOREIGN KEY(id_usuario) REFERENCES Usuario(id) ON DELETE CASCADE
    );''')

    # Crear tabla tarea_archivos para almacenar archivos subidos por trabajadores
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tarea_archivos (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      tarea_id INTEGER NOT NULL,
      usuario_id INTEGER NOT NULL,
      nombre_archivo TEXT NOT NULL,
      ruta_archivo TEXT NOT NULL,
      fecha_subida DATETIME DEFAULT CURRENT_TIMESTAMP,
      FOREIGN KEY(tarea_id) REFERENCES tareas(id) ON DELETE CASCADE,
      FOREIGN KEY(usuario_id) REFERENCES Usuario(id) ON DELETE CASCADE
    );''')

    conn.commit()
    conn.close()

# Execute function when starting the app
crear_tabla_usuario()

# Register error handlers
register_error_handlers(app)

# Register monitoring routes (for administrators)
register_monitoring_routes(app)

# Register security middleware
register_security_middleware(app)

# Configure rate limiting
setup_rate_limiting(app)

# Rutas principales
@app.route('/')
def landing():
    return render_template('landingpage.html')

@app.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('avatars/logo.png')

@app.route('/administrador')
@admin_required
def administrador():
    return render_template('admin.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing'))

if __name__ == '__main__':
    app.run(debug=True)


