# --- CHATBOX: Rutas para chat trabajador → líder ---
from flask import current_app
from flask import Blueprint, request, jsonify
from app.session_decorators import api_trabajador_required
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv
import os
from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
import time
import sqlite3
import os
from datetime import datetime
import uuid
from werkzeug.utils import secure_filename
from app.session_decorators import trabajador_required, api_trabajador_required, secure_route

trabajador_blueprint = Blueprint('trabajador', __name__)



@trabajador_blueprint.route('/trabajador')
@secure_route(allowed_roles=['trabajador'])
def trabajador():

    usuario = session.get('usuario')
    grupo_usuario = session.get('grupo')
    print(f"ID usuario logueado: {usuario}, Grupo: '{grupo_usuario}'")

    # Si la sesión es dict (nuevo formato), extraer el id
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
        usuario_nombre = usuario.get('nombre_usuario')
    else:
        usuario_id = usuario
        usuario_nombre = usuario

    # Asegurar que usuario_id sea un entero válido
    try:
        if usuario_id is not None:
            usuario_id = int(usuario_id)
    except (ValueError, TypeError):
        print(f"Error: usuario_id no válido: {usuario_id}")
        return redirect(url_for('login.login'))

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    # Obtener datos de perfil del usuario
    print('DEBUG usuario_id en sesión:', usuario_id, type(usuario_id))
    usuario_row = None
    if usuario_id is not None:
        usuario_row = conn.execute(
            'SELECT nombre_completo FROM Usuario WHERE id = ?', (usuario_id,)
        ).fetchone()
        
    if usuario_row:
        nombre_usuario = usuario_row['nombre_completo'] or 'Usuario'
        avatar_url = '/static/avatars/perfil_predeterminado.png'
        acerca_de_mi = ''
    else:
        nombre_usuario = 'Usuario'
        avatar_url = '/static/avatars/perfil_predeterminado.png'
        acerca_de_mi = ''

    proyecto_row = conn.execute(
        'SELECT proyecto FROM Usuario WHERE id = ?', (usuario_id,)
    ).fetchone()
    nombre_proyecto = proyecto_row['proyecto'] if proyecto_row else "Sin proyecto asignado"

    cursos = conn.execute('SELECT DISTINCT curso_destino FROM tareas').fetchall()
    for c in cursos:
        print(f"'{c['curso_destino']}'")

    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()

    proyectos = conn.execute('SELECT * FROM Proyecto').fetchall()
    conn.close()

    print(f"Tareas encontradas: {tareas}")

    # Procesar tareas
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        dt = None
        if fecha:
            for fmt in ('%Y-%m-%d', '%d/%m/%Y', '%d-%m-%Y'):
                try:
                    dt = datetime.strptime(fecha, fmt)
                    break
                except ValueError:
                    continue
        if dt:
            tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')

        # Archivo asociado a la tarea (usando el campo ruta_archivo de la BD)
        archivos = []
        if tarea_dict.get('ruta_archivo'):
            # Verificar que el archivo realmente existe en el sistema de archivos
            ruta_completa = os.path.join('static', tarea_dict['ruta_archivo'])
            if os.path.exists(ruta_completa):
                nombre_archivo = os.path.basename(tarea_dict['ruta_archivo'])
                archivos.append({
                    'nombre': nombre_archivo,
                    'url': f'/static/{tarea_dict["ruta_archivo"]}'
                })
        tarea_dict['archivos'] = archivos
        tareas_list.append(tarea_dict)

    return render_template(
        'trabajador.html',
        tareas=tareas_list,
        proyectos=proyectos,
        nombre_proyecto=nombre_proyecto,
        nombre_usuario=nombre_usuario,
        avatar_url=avatar_url,
        acerca_de_mi=acerca_de_mi,
        now=int(time.time())
    )

def notificar_lider_tarea_completada(tarea_id):
    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    # Obtener info de la tarea y el usuario asignado
    cur.execute('SELECT titulo, id_usuario_asignado, curso_destino FROM tareas WHERE id = ?', (tarea_id,))
    tarea = cur.fetchone()
    if not tarea:
        conn.close()
        return
    titulo, id_usuario_asignado, curso_destino = tarea
    # Buscar líder por grupo (curso_destino) o por proyecto si lo tienes
    cur.execute('''
        SELECT id, correo FROM Usuario
        WHERE rol = 'lider' AND TRIM(LOWER(grupo)) = TRIM(LOWER(?))
    ''', (curso_destino,))
    lider = cur.fetchone()
    if not lider:
        conn.close()
        return
    id_lider, correo_lider = lider
    # Insertar notificación en la base de datos
    mensaje = f'La tarea "{titulo}" ha sido completada por el trabajador.'
    cur.execute('INSERT INTO notificaciones (mensaje, id_usuario) VALUES (?, ?)', (mensaje, id_lider))
    conn.commit()
    conn.close()
    # Enviar correo
    try:
        from app.email_service import enviar_notificacion_lider
        enviar_notificacion_lider(correo_lider, 'Tarea completada', mensaje)
    except Exception as e:
        print('Error enviando email al líder:', e)

# --- API para marcar tarea como completada ---
@trabajador_blueprint.route('/api/tarea/completar/<int:tarea_id>', methods=['POST'])
@api_trabajador_required
def completar_tarea(tarea_id):
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        conn.commit()
        conn.close()
        notificar_lider_tarea_completada(tarea_id)
        return jsonify({'ok': True})
    except Exception as e:
        return jsonify({'ok': False, 'msg': str(e)}), 500


# --- API: Actualizar Perfil (nombre, acerca_de_mi, avatar) ---

# --- CHATBOX: Rutas para chat trabajador → líder ---
from flask import current_app


# (Eliminada función duplicada de /api/usuarios/chat)

# Obtener mensajes entre trabajador y líder

# API: Mensajes entre trabajador y su líder
@trabajador_blueprint.route('/api/chat/<int:receptor_id>', methods=['GET'])
@api_trabajador_required
def obtener_mensajes_chat_trabajador(receptor_id):
    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    if not usuario_id:
        return jsonify([])
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    # Solo mensajes entre el trabajador logueado y el líder receptor
    cursor.execute('''
        SELECT m.*, u.nombre_completo as emisor_nombre, u.rol as emisor_rol
        FROM mensajes m
        JOIN Usuario u ON m.emisor_id = u.id
        WHERE (m.emisor_id = ? AND m.receptor_id = ?)
           OR (m.emisor_id = ? AND m.receptor_id = ?)
        ORDER BY m.fecha ASC
    ''', (usuario_id, receptor_id, receptor_id, usuario_id))
    mensajes = cursor.fetchall()
    conn.close()
    return jsonify([dict(m) for m in mensajes])

# Enviar mensaje de trabajador a líder

# API: Enviar mensaje de trabajador a líder
@trabajador_blueprint.route('/api/chat/enviar', methods=['POST'])
@api_trabajador_required
def enviar_mensaje_trabajador():
    data = request.get_json()
    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        emisor_id = usuario.get('id')
    else:
        emisor_id = usuario
    receptor_id = data.get('receptor_id')
    mensaje = data.get('mensaje')
    if not emisor_id or not receptor_id or not mensaje:
        return jsonify({'error': 'Datos incompletos'}), 400
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    # Validar roles
    cursor.execute('SELECT rol FROM Usuario WHERE id = ?', (emisor_id,))
    rol_emisor = cursor.fetchone()
    cursor.execute('SELECT rol FROM Usuario WHERE id = ?', (receptor_id,))
    rol_receptor = cursor.fetchone()
    if not rol_emisor or not rol_receptor or rol_emisor[0] != 'trabajador' or rol_receptor[0] != 'lider':
        conn.close()
        return jsonify({'error': 'Solo se permite enviar mensajes de trabajador a líder'}), 403
    cursor.execute('SELECT nombre_completo FROM Usuario WHERE id = ?', (emisor_id,))
    emisor_nombre = cursor.fetchone()[0]
    cursor.execute('''
        INSERT INTO mensajes (emisor_id, emisor, receptor_id, mensaje, tipo)
        VALUES (?, ?, ?, ?, 'texto')
    ''', (emisor_id, emisor_nombre, receptor_id, mensaje))
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@trabajador_blueprint.route('/api/actualizar_perfil', methods=['POST'])
@api_trabajador_required
def api_actualizar_perfil():
    nombre = request.form.get('nombre')
    acerca_de_mi = request.form.get('descripcion')
    avatar = request.files.get('avatar')
    avatar_url = None

    # Obtener usuario actual
    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    if not usuario_id:
        return jsonify({'success': False, 'error': 'No autenticado'}), 401

    # Guardar avatar si se subió
    if avatar:
        ext = os.path.splitext(avatar.filename)[1]
        filename = f"{uuid.uuid4()}{ext}"
        avatars_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'avatars')
        os.makedirs(avatars_folder, exist_ok=True)
        avatar_path = os.path.join(avatars_folder, filename)
        avatar.save(avatar_path)
        avatar_url = f"/static/avatars/{filename}"

    # Actualizar en la base de datos
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    if nombre:
        cursor.execute("UPDATE Usuario SET nombre_completo = ? WHERE id = ?", (nombre, usuario_id))
    if acerca_de_mi is not None:
        try:
            cursor.execute("ALTER TABLE Usuario ADD COLUMN acerca_de_mi TEXT")
        except Exception:
            pass
        cursor.execute("UPDATE Usuario SET acerca_de_mi = ? WHERE id = ?", (acerca_de_mi, usuario_id))
    if avatar_url:
        try:
            cursor.execute("ALTER TABLE Usuario ADD COLUMN avatar_url TEXT")
        except Exception:
            pass
        cursor.execute("UPDATE Usuario SET avatar_url = ? WHERE id = ?", (avatar_url, usuario_id))
    conn.commit()

    # Obtener los datos actualizados de la base de datos
    usuario_row = cursor.execute(
        "SELECT nombre_completo, avatar_url, acerca_de_mi FROM Usuario WHERE id = ?", (usuario_id,)
    ).fetchone()
    conn.close()

    nombre_actual = usuario_row[0] if usuario_row and usuario_row[0] else nombre or ''
    avatar_url_actual = usuario_row[1] if usuario_row and usuario_row[1] else '/static/avatars/perfil_predeterminado.png'
    acerca_de_mi_actual = usuario_row[2] if usuario_row and usuario_row[2] else acerca_de_mi or ''

    return jsonify({
        'success': True,
        'nombre': nombre_actual,
        'acerca_de_mi': acerca_de_mi_actual,
        'avatar_url': avatar_url_actual
    })

# --- API para subir archivo a tarea ---
@trabajador_blueprint.route('/api/tarea/subir-archivo/<int:tarea_id>', methods=['POST'])
@api_trabajador_required
def subir_archivo_tarea(tarea_id):
    if 'archivo' not in request.files:
        return jsonify({'ok': False, 'msg': 'No se envió archivo'}), 400
    archivo = request.files['archivo']
    if archivo.filename == '':
        return jsonify({'ok': False, 'msg': 'Nombre de archivo vacío'}), 400
    
    # Obtener información del usuario
    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
        usuario_nombre = usuario.get('nombre_usuario')
    else:
        usuario_id = usuario
        usuario_nombre = usuario
    if not usuario_id:
        # Si no tienes usuario_id en sesión, obtenerlo de la base de datos
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        cur.execute('SELECT id FROM Usuario WHERE nombre_usuario = ?', (usuario_nombre,))
        result = cur.fetchone()
        conn.close()
        if result:
            usuario_id = result[0]
        else:
            return jsonify({'ok': False, 'msg': 'Usuario no encontrado'}), 400
    
    carpeta_destino = os.path.join('static', 'archivos_tareas')
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
    
    # Crear nombre único para el archivo
    nombre_archivo_original = archivo.filename
    nombre_archivo = f"{tarea_id}_{usuario_id}_{archivo.filename}"
    ruta_destino = os.path.join(carpeta_destino, nombre_archivo)
    ruta_relativa = f"archivos_tareas/{nombre_archivo}"
    
    print(f"=== DEBUG SUBIDA DE ARCHIVO ===")
    print(f"Tarea ID: {tarea_id}")
    print(f"Usuario ID: {usuario_id}")
    print(f"Archivo original: {nombre_archivo_original}")
    print(f"Nombre final: {nombre_archivo}")
    print(f"Ruta destino: {ruta_destino}")
    print(f"Ruta relativa: {ruta_relativa}")
    
    # Guardar el archivo físicamente
    archivo.save(ruta_destino)
    print(f"Archivo guardado en: {ruta_destino}")
    
    # Verificar que el archivo se guardó
    if os.path.exists(ruta_destino):
        print(f"✅ Archivo confirmado en sistema de archivos")
    else:
        print(f"❌ ERROR: Archivo NO encontrado en sistema de archivos")
    
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cur = conn.cursor()
        
        # Insertar el archivo en la tabla tarea_archivos
        cur.execute('''
            INSERT INTO tarea_archivos (tarea_id, usuario_id, nombre_archivo, ruta_archivo)
            VALUES (?, ?, ?, ?)
        ''', (tarea_id, usuario_id, nombre_archivo_original, ruta_relativa))
        print(f"✅ Registro insertado en tarea_archivos")
        
        # Marcar la tarea como completada
        cur.execute('UPDATE tareas SET estado = ? WHERE id = ?', ('completado', tarea_id))
        print(f"✅ Tarea {tarea_id} marcada como completada")
        
        conn.commit()
        conn.close()
        
        # Notificar al líder
        notificar_lider_tarea_completada(tarea_id)
        
    except Exception as e:
        return jsonify({'ok': False, 'msg': f'Archivo subido pero error al actualizar base de datos: {str(e)}'}), 500
    
    return jsonify({
        'ok': True, 
        'nombre': nombre_archivo_original, 
        'url': '/' + ruta_destino.replace('\\', '/')
    })

# --- API para obtener detalles de tarea ---
@trabajador_blueprint.route('/api/tarea/<int:tarea_id>')
@api_trabajador_required
def api_tarea_detalle(tarea_id):
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tarea = conn.execute('SELECT * FROM tareas WHERE id = ?', (tarea_id,)).fetchone()
    archivos = []
    # Si tienes una tabla de archivos, aquí deberías consultarla. Si no, deja vacío o busca en carpeta.
    # Ejemplo: buscar archivos en static/archivos_tareas/ que empiecen con el id de la tarea
    carpeta = os.path.join('static', 'archivos_tareas')
    if os.path.exists(carpeta):
        for nombre in os.listdir(carpeta):
            if nombre.startswith(f'{tarea_id}_') or nombre.startswith(f'{tarea_id}-') or nombre.startswith(f'{tarea_id}'):  # Ajusta según tu convención
                archivos.append({
                    'nombre': nombre,
                    'url': f'/static/archivos_tareas/{nombre}'
                })
    conn.close()
    if not tarea:
        return jsonify({'ok': False, 'msg': 'Tarea no encontrada'}), 404
    tarea_dict = dict(tarea)
    tarea_dict['archivos'] = archivos
    return jsonify(tarea_dict)

# --- API para obtener todas las tareas del usuario ---
@trabajador_blueprint.route('/api/tareas')
@api_trabajador_required
def api_tareas_usuario():
    usuario = session.get('usuario')
    grupo_usuario = session.get('grupo')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    tareas = conn.execute('''
        SELECT * FROM tareas
        WHERE id_usuario_asignado = ? OR TRIM(LOWER(curso_destino)) = TRIM(LOWER(?))
    ''', (usuario_id, grupo_usuario)).fetchall()
    conn.close()
    tareas_list = []
    for t in tareas:
        tarea_dict = dict(t)
        fecha = tarea_dict.get('fecha_vencimiento')
        if fecha:
            try:
                dt = datetime.strptime(fecha, '%Y-%m-%d')
            except ValueError:
                try:
                    dt = datetime.strptime(fecha, '%d/%m/%Y')
                except ValueError:
                    try:
                        dt = datetime.strptime(fecha, '%d-%m-%Y')
                    except ValueError:
                        dt = None
            if dt:
                tarea_dict['fecha_vencimiento'] = dt.strftime('%Y-%m-%d')
        # Buscar todos los archivos asociados a la tarea
        carpeta = os.path.join('static', 'archivos_tareas')
        archivos = []
        if os.path.exists(carpeta):
            for nombre in os.listdir(carpeta):
                if nombre.startswith(f"{t['id']}_") or nombre.startswith(f"{t['id']}-") or nombre.startswith(f"{t['id']}"):
                    archivos.append({
                        'nombre': nombre,
                        'url': f'/static/archivos_tareas/{nombre}'
                    })
        tarea_dict['archivos'] = archivos
        # (Opcional) Mantener ruta_archivo para compatibilidad, pero solo el primero
        tarea_dict['ruta_archivo'] = archivos[0]['nombre'] if archivos else None
        tareas_list.append(tarea_dict)
    return jsonify(tareas_list)


# --- ENDPOINT DE DEPURACIÓN: Verificar archivos en base de datos ---
@trabajador_blueprint.route('/api/debug/archivos')
@api_trabajador_required
def debug_archivos():
    
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    
    # Verificar si la tabla existe
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tarea_archivos';")
    tabla_existe = cursor.fetchone()
    
    if not tabla_existe:
        conn.close()
        return jsonify({
            'ok': False, 
            'msg': 'La tabla tarea_archivos no existe',
            'archivos': []
        })
    
    # Obtener todos los archivos
    cursor.execute('''
        SELECT ta.*, u.usuario, t.titulo 
        FROM tarea_archivos ta
        LEFT JOIN Usuario u ON ta.usuario_id = u.id
        LEFT JOIN tareas t ON ta.tarea_id = t.id
        ORDER BY ta.fecha_subida DESC
    ''')
    archivos = cursor.fetchall()
    
    archivos_list = []
    for archivo in archivos:
        archivos_list.append({
            'id': archivo[0],
            'tarea_id': archivo[1],
            'usuario_id': archivo[2],
            'nombre_archivo': archivo[3],
            'ruta_archivo': archivo[4],
            'fecha_subida': archivo[5],
            'usuario': archivo[6] if len(archivo) > 6 else 'Desconocido',
            'titulo_tarea': archivo[7] if len(archivo) > 7 else 'Desconocido'
        })
    
    conn.close()
    
    return jsonify({
        'ok': True,
        'total_archivos': len(archivos_list),
        'archivos': archivos_list
    })


# --- ENDPOINT DE DEPURACIÓN: Listar archivos físicos ---
@trabajador_blueprint.route('/api/debug/archivos-fisicos')
@api_trabajador_required
def debug_archivos_fisicos():
    
    carpeta = os.path.join('static', 'archivos_tareas')
    archivos_fisicos = []
    
    if os.path.exists(carpeta):
        for nombre in os.listdir(carpeta):
            ruta_completa = os.path.join(carpeta, nombre)
            if os.path.isfile(ruta_completa):
                stat = os.stat(ruta_completa)
                archivos_fisicos.append({
                    'nombre': nombre,
                    'tamaño': stat.st_size,
                    'fecha_modificacion': stat.st_mtime
                })
    
    return jsonify({
        'ok': True,
        'carpeta': carpeta,
        'total_archivos': len(archivos_fisicos),
        'archivos': archivos_fisicos
    })

# --- API para obtener notificaciones del trabajador ---
@trabajador_blueprint.route('/api/notificaciones')
@api_trabajador_required
def api_notificaciones_trabajador():
    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    notificaciones = conn.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (usuario_id,)).fetchall()
    conn.close()
    return jsonify({'ok': True, 'notificaciones': [dict(n) for n in notificaciones]})

@trabajador_blueprint.route('/api/actualizar_foto', methods=['POST'])
@api_trabajador_required
def actualizar_foto_trabajador():
    file = request.files.get('avatar')
    descripcion = request.form.get('descripcion')  # <-- obtener el campo descripcion
    if not file:
        return jsonify({'success': False, 'error': 'No se envió archivo'}), 400

    filename = secure_filename(file.filename)
    # Usar uuid para evitar colisiones
    ext = os.path.splitext(filename)[1]
    filename = f"{uuid.uuid4()}{ext}"
    upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)

    usuario = session.get('usuario')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE Usuario SET foto = ? WHERE id = ?", (filename, usuario_id))
    # Si se envía descripcion, actualizarla también
    if descripcion is not None:
        cursor.execute("UPDATE Usuario SET descripcion = ? WHERE id = ?", (descripcion, usuario_id))
    cursor.execute("SELECT nombre_completo, descripcion FROM Usuario WHERE id = ?", (usuario_id,))
    row = cursor.fetchone()
    conn.commit()
    conn.close()

    session['foto'] = filename

    foto_url = url_for('static', filename='uploads/' + filename) + '?t=' + str(int(os.path.getmtime(file_path)))
    nombre = row[0] if row else ''
    acerca_de_mi = row[1] if row else ''
    return jsonify({'success': True, 'foto_url': foto_url, 'nombre': nombre, 'acerca_de_mi': acerca_de_mi})


@trabajador_blueprint.route('/enviar_reporte', methods=['POST'])
def enviar_reporte():
    # Usar la configuración Gmail del .env
    email_destino = os.getenv('GMAIL_USERNAME')
    email_password = os.getenv('GMAIL_PASSWORD')
    email_host = os.getenv('GMAIL_HOST', 'smtp.gmail.com')
    email_port = int(os.getenv('GMAIL_PORT', '587'))
    
    # Validar que las credenciales estén configuradas
    if not email_destino or not email_password:
        return jsonify({'ok': False, 'error': 'Configuración de Gmail no encontrada en variables de entorno'}), 500

    usuario = session.get('usuario')
    if not usuario or not isinstance(usuario, dict) or 'email' not in usuario:
        return jsonify({'ok': False, 'error': 'Usuario no autenticado'}), 401
    remitente = usuario['email']

    try:
        # Obtener datos del formulario
        asunto = request.form.get('asunto', '').strip()
        tipo = request.form.get('tipo', '').strip()
        descripcion = request.form.get('descripcion', '').strip()
        archivo = request.files.get('archivo')

        # Validar campos obligatorios
        if not asunto or not descripcion:
            return jsonify({'ok': False, 'error': 'Asunto y descripción son obligatorios.'}), 400

        # Validar archivo adjunto si existe
        adjunto_bytes = None
        adjunto_nombre = None
        adjunto_mime = None
        if archivo:
            allowed = {'application/pdf', 'image/png', 'image/jpeg'}
            if archivo.mimetype not in allowed:
                return jsonify({'ok': False, 'error': 'Tipo de archivo no permitido. Solo PDF, PNG o JPG.'}), 400
            archivo.seek(0, 2)
            size = archivo.tell()
            archivo.seek(0)
            if size > 5 * 1024 * 1024:
                return jsonify({'ok': False, 'error': 'El archivo supera el tamaño máximo de 5 MB.'}), 400
            adjunto_bytes = archivo.read()
            adjunto_nombre = secure_filename(archivo.filename)
            adjunto_mime = archivo.mimetype

        # Validar configuración SMTP
        if not all([email_destino, email_password, email_host, email_port]):
            return jsonify({'ok': False, 'error': 'Configuración SMTP incompleta'}), 500

        # Crear mensaje de email
        msg = EmailMessage()
        msg['Subject'] = f"[Soporte] {asunto}"
        msg['From'] = email_destino  # El remitente SMTP es la cuenta de soporte
        msg['To'] = email_destino
        cuerpo = f"""
Se ha recibido un nuevo reporte de soporte:

Remitente (usuario autenticado): {remitente}
Tipo de problema: {tipo}
Asunto: {asunto}
Descripción:
{descripcion}
"""
        msg.set_content(cuerpo)
        if adjunto_bytes:
            msg.add_attachment(adjunto_bytes, maintype=adjunto_mime.split('/')[0], subtype=adjunto_mime.split('/')[1], filename=adjunto_nombre)

        # Enviar email
        try:
            with smtplib.SMTP(email_host, email_port) as smtp:
                smtp.starttls()
                smtp.login(email_destino, email_password)
                smtp.send_message(msg)
        except smtplib.SMTPAuthenticationError:
            return jsonify({'ok': False, 'error': 'Credenciales SMTP inválidas.'}), 500
        except Exception as e:
            return jsonify({'ok': False, 'error': f'Error enviando email: {str(e)}'}), 500

        return jsonify({'ok': True})
    except Exception as ex:
        return jsonify({'ok': False, 'error': str(ex)}), 500

# --- API para obtener usuarios para chat ---
@trabajador_blueprint.route('/api/usuarios/chat')
@api_trabajador_required
def api_usuarios_chat():
    """Devuelve solo el líder del grupo del trabajador logueado"""
    usuario = session.get('usuario')
    grupo_usuario = session.get('grupo')
    if isinstance(usuario, dict):
        usuario_id = usuario.get('id')
    else:
        usuario_id = usuario
    if not grupo_usuario:
        return jsonify([])
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT id, nombre_completo, rol, foto
        FROM Usuario
        WHERE estado = 'activo' AND rol = 'lider' AND TRIM(LOWER(grupo)) = TRIM(LOWER(?))
        LIMIT 1
    ''', (grupo_usuario,))
    lider = cursor.fetchone()
    conn.close()
    if lider:
        return jsonify([dict(lider)])
    else:
        return jsonify([])

