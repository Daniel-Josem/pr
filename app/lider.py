from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from fpdf import FPDF
import tempfile
from datetime import datetime
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash,check_password_hash
import sqlite3
import os
from io import BytesIO
from werkzeug.utils import secure_filename
from app.session_decorators import lider_required, secure_route

lider = Blueprint('lider', __name__)

def limpiar_archivos_huerfanos():
    """
    Elimina archivos de la carpeta archivos_tareas que ya no están vinculados a ninguna tarea.
    """
    try:
        conn = sqlite3.connect('gestor_de_tareas.db')
        cursor = conn.cursor()
        
        # Obtener todas las rutas de archivos vinculadas a tareas
        cursor.execute('SELECT ruta_archivo FROM tareas WHERE ruta_archivo IS NOT NULL')
        archivos_vinculados = {row[0] for row in cursor.fetchall()}
        conn.close()
        
        # Obtener todos los archivos en la carpeta
        carpeta_archivos = os.path.join('static', 'archivos_tareas')
        if os.path.exists(carpeta_archivos):
            for nombre_archivo in os.listdir(carpeta_archivos):
                ruta_relativa = f"archivos_tareas/{nombre_archivo}"
                ruta_completa = os.path.join(carpeta_archivos, nombre_archivo)
                
                # Si el archivo no está vinculado a ninguna tarea, eliminarlo
                if ruta_relativa not in archivos_vinculados:
                    try:
                        os.remove(ruta_completa)
                        print(f"Archivo huérfano eliminado: {nombre_archivo}")
                    except OSError as e:
                        print(f"Error al eliminar archivo huérfano {nombre_archivo}: {e}")
    except Exception as e:
        print(f"Error en limpiar_archivos_huerfanos: {e}")

# Crear tarea
@lider.route('/crear_tarea', methods=['POST'])
@lider_required
def crear_tarea():

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    ruta_archivo = None
    if archivo and archivo.filename != '':
        # Generar nombre único para evitar conflictos
        filename = secure_filename(archivo.filename)
        nombre, extension = os.path.splitext(filename)
        
        # Insertar la tarea primero para obtener el ID
        cursor.execute('INSERT INTO tareas (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, fecha_registro) VALUES (?, ?, ?, ?, ?, ?, DATE("now"))', 
                       (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado))
        
        tarea_id = cursor.lastrowid
        
        # Crear nombre único usando el ID de la tarea
        filename_unico = f"{tarea_id}_{filename}"
        ruta_archivo = f"archivos_tareas/{filename_unico}"
        
        # Crear directorio si no existe
        upload_dir = os.path.join('static', 'archivos_tareas')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Guardar el archivo con el nombre único
        archivo.save(os.path.join('static', ruta_archivo))
        
        # Actualizar la tarea con la ruta del archivo
        cursor.execute('UPDATE tareas SET ruta_archivo = ? WHERE id = ?', (ruta_archivo, tarea_id))
    else:
        # Si no hay archivo, insertar la tarea normalmente
        cursor.execute('INSERT INTO tareas (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo, fecha_registro) VALUES (?, ?, ?, ?, ?, ?, ?, DATE("now"))', 
                       (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, None))

    conn.commit()
    conn.close()

    flash('Tarea creada exitosamente')
    return redirect(url_for('lider.lideres'))

# Mostrar tareas
@lider.route('/lider')
@secure_route(allowed_roles=['lider'])
def lideres():
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    grupo_lider = session.get('grupo')
    usuario_sesion = session.get('usuario')
    usuario_id = session.get('usuario_id')

    # Obtener información completa del usuario desde la BD
    usuario_info = conn.execute('SELECT * FROM Usuario WHERE id = ?', (usuario_id,)).fetchone()

    if not usuario_info:
        flash('Error al cargar información del usuario', 'error')
        return redirect(url_for('login.login'))

    nombre_lider = usuario_info['nombre_completo']
    correo_lider = usuario_info['correo']

    # 🔥 Convertir tareas a diccionarios
    tareas_db = conn.execute('SELECT * FROM tareas WHERE LOWER(curso_destino) = LOWER(?)', (grupo_lider,)).fetchall()
    tareas = [dict(tarea) for tarea in tareas_db]

    # 🔥 Convertir proyectos a diccionarios
    proyectos_db = conn.execute('SELECT * FROM Proyecto WHERE LOWER(grupo) = LOWER(?)', (grupo_lider,)).fetchall()
    proyectos = [dict(proyecto) for proyecto in proyectos_db]

    # Solo usuarios del grupo con rol 'trabajador'
    usuarios_por_grupo = {grupo_lider: []}
    usuarios_db = conn.execute('SELECT nombre_completo, nombre_usuario, correo, grupo, rol FROM Usuario WHERE LOWER(grupo) = LOWER(?)', (grupo_lider,)).fetchall()
    usuarios = [dict(usuario) for usuario in usuarios_db]

    for usuario in usuarios:
        if usuario['rol'].lower().strip() == 'trabajador':
            usuarios_por_grupo[grupo_lider].append(usuario)

    # 🔔 Contar solo notificaciones no leídas del grupo
    notificaciones = conn.execute('''
        SELECT COUNT(*) AS cantidad
        FROM notificaciones n
        JOIN Usuario u ON n.id_usuario = u.id
        WHERE LOWER(u.grupo) = LOWER(?) AND n.leido = 0
    ''', (grupo_lider,)).fetchone()

    cantidad_notificaciones = notificaciones['cantidad']

    conn.close()

    return render_template('lider.html',
                           tareas=tareas,
                           proyectos=proyectos,
                           usuarios_por_grupo=usuarios_por_grupo,
                           nombre_usuario=nombre_lider,
                           correo_usuario=correo_lider,
                           grupo_lider=grupo_lider,
                           cantidad_notificaciones=cantidad_notificaciones)


# Editar tarea
@lider.route('/editar_tarea', methods=['POST'])
@lider_required
def editar_tarea():

    id_tarea = request.form['id']
    titulo = request.form['titulo']
    descripcion = request.form['descripcion']
    curso_destino = request.form['curso_destino']
    fecha_vencimiento = request.form['fecha_vencimiento']
    prioridad = request.form['prioridad']
    estado = request.form['estado']

    archivo = request.files['archivo']
    ruta_archivo = None

    if archivo and archivo.filename != '':
        filename = secure_filename(archivo.filename)
        # Crear nombre único usando el ID de la tarea
        filename_unico = f"{id_tarea}_{filename}"
        ruta_archivo = f"archivos_tareas/{filename_unico}"
        
        # Crear directorio si no existe
        upload_dir = os.path.join('static', 'archivos_tareas')
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        # Obtener la ruta del archivo anterior para eliminarlo si existe
        cursor.execute('SELECT ruta_archivo FROM tareas WHERE id = ?', (id_tarea,))
        archivo_anterior = cursor.fetchone()
        if archivo_anterior and archivo_anterior[0]:
            ruta_anterior = os.path.join('static', archivo_anterior[0])
            if os.path.exists(ruta_anterior):
                try:
                    os.remove(ruta_anterior)
                except OSError:
                    pass  # Continuar aunque no se pueda eliminar el archivo anterior
        
        # Guardar el nuevo archivo
        archivo.save(os.path.join('static', ruta_archivo))

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    if ruta_archivo:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?, ruta_archivo = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, ruta_archivo, id_tarea))
    else:
        cursor.execute('''
            UPDATE tareas 
            SET titulo = ?, descripcion = ?, curso_destino = ?, fecha_vencimiento = ?, prioridad = ?, estado = ?
            WHERE id = ?
        ''', (titulo, descripcion, curso_destino, fecha_vencimiento, prioridad, estado, id_tarea))

    conn.commit()
    conn.close()

    flash('Tarea actualizada exitosamente')
    return redirect(url_for('lider.lideres'))

# Eliminar tarea
@lider.route('/eliminar_tarea/<int:id>', methods=['POST'])
@lider_required
def eliminar_tarea(id):

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Obtener la ruta del archivo para eliminarlo
    cursor.execute('SELECT ruta_archivo FROM tareas WHERE id = ?', (id,))
    resultado = cursor.fetchone()
    if resultado and resultado[0]:
        ruta_archivo = os.path.join('static', resultado[0])
        if os.path.exists(ruta_archivo):
            try:
                os.remove(ruta_archivo)
            except OSError:
                pass  # Continuar aunque no se pueda eliminar el archivo

    cursor.execute('DELETE FROM tareas WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    # Limpiar archivos huérfanos después de eliminar la tarea
    limpiar_archivos_huerfanos()

    flash('Tarea eliminada exitosamente')
    return redirect(url_for('lider.lideres'))

@lider.route('/crear_proyecto', methods=['POST'])
@lider_required
def crear_proyecto():

    nombre = request.form['nombre']
    descripcion = request.form['descripcion']
    fecha_inicio = request.form['fecha_inicio']
    fecha_fin = request.form['fecha_fin']
    grupo_lider = session.get('grupo')  # Obtener el grupo del líder

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Proyecto (nombre, descripcion, grupo, fecha_inicio, fecha_fin) VALUES (?, ?, ?, ?, ?)',
                   (nombre, descripcion, grupo_lider, fecha_inicio, fecha_fin))
    conn.commit()
    conn.close()

    flash('Proyecto creado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))  # Esto debe estar así para recargar la vista

@lider.route('/eliminar_proyecto/<int:id>', methods=['POST'])
@lider_required
def eliminar_proyecto(id):

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    # Desvincular las tareas del proyecto eliminado
    cursor.execute('UPDATE tareas SET id_proyecto = NULL WHERE id_proyecto = ?', (id,))

    cursor.execute('DELETE FROM Proyecto WHERE id = ?', (id,))
    conn.commit()
    conn.close()

    flash('Proyecto eliminado exitosamente', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/asignar_tarea_a_proyecto', methods=['POST'])
@lider_required
def asignar_tarea_a_proyecto():

    tarea_id = request.form['tarea_id']
    proyecto_id = request.form['proyecto_id']

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    cursor.execute('UPDATE tareas SET id_proyecto = ? WHERE id = ?', (proyecto_id, tarea_id))
    conn.commit()
    conn.close()

    flash('Tarea asignada exitosamente al proyecto', 'success')
    return redirect(url_for('lider.lideres'))

@lider.route('/notificaciones')
@lider_required
def ver_notificaciones():
    usuario = session['usuario']
    id_lider = usuario['id']  # 🔥 Ya no necesitas buscarlo, ya lo tienes

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Obtener notificaciones para el líder
    cur.execute('SELECT * FROM notificaciones WHERE id_usuario = ? ORDER BY id DESC', (id_lider,))
    notificaciones = cur.fetchall()
    conn.close()

    return {'notificaciones': [dict(n) for n in notificaciones]}

@lider.route('/notificaciones/marcar_leida', methods=['POST'])
@lider_required
def marcar_notificacion_leida():
    data = request.get_json()
    notificacion_id = data.get('id')
    if not notificacion_id:
        return {'success': False, 'error': 'ID requerido'}, 400

    conn = sqlite3.connect('gestor_de_tareas.db')
    cur = conn.cursor()
    cur.execute('UPDATE notificaciones SET leido = 1 WHERE id = ?', (notificacion_id,))
    conn.commit()
    conn.close()

    return {'success': True}


@lider.route('/api/tarea/<int:tarea_id>/archivos')
@lider_required
def obtener_archivos_tarea(tarea_id):

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()

    try:
        # Obtener información de la tarea
        cursor.execute('SELECT titulo, curso_destino FROM tareas WHERE id = ?', (tarea_id,))
        tarea_info = cursor.fetchone()
        
        if not tarea_info:
            return jsonify({'error': 'Tarea no encontrada'}), 404

        titulo_tarea, curso_destino = tarea_info

        # Obtener archivos subidos por trabajadores
        cursor.execute('''
            SELECT 
                ta.nombre_archivo,
                ta.ruta_archivo,
                ta.fecha_subida,
                u.nombre_completo,
                u.nombre_usuario
            FROM tarea_archivos ta
            JOIN Usuario u ON ta.usuario_id = u.id
            WHERE ta.tarea_id = ?
            ORDER BY ta.fecha_subida DESC
        ''', (tarea_id,))
        
        archivos_raw = cursor.fetchall()
        archivos = []
        for archivo in archivos_raw:
            nombre_archivo, ruta_archivo, fecha_subida, nombre_completo, usuario = archivo
            archivos.append({
                'nombre': nombre_archivo,
                'url': f'/static/{ruta_archivo}' if ruta_archivo else '#',
                'fecha_subida': fecha_subida,
                'usuario': nombre_completo or usuario
            })

        # Estadísticas
        cursor.execute('SELECT COUNT(*) FROM Usuario WHERE grupo = ?', (curso_destino,))
        total_trabajadores = cursor.fetchone()[0]

        cursor.execute('''
            SELECT COUNT(DISTINCT ta.usuario_id) 
            FROM tarea_archivos ta 
            WHERE ta.tarea_id = ?
        ''', (tarea_id,))
        tareas_completadas = cursor.fetchone()[0]

        tareas_pendientes = total_trabajadores - tareas_completadas

        estadisticas = {
            'total_trabajadores': total_trabajadores,
            'tareas_completadas': tareas_completadas,
            'tareas_pendientes': tareas_pendientes
        }

        return jsonify({
            'archivos': archivos,
            'estadisticas': estadisticas,
            'tarea': {
                'id': tarea_id,
                'titulo': titulo_tarea,
                'curso': curso_destino
            }
        })

    except Exception as e:
        print(f"Error al obtener archivos de tarea {tarea_id}: {e}")
        return jsonify({'error': 'Error interno del servidor'}), 500
    finally:
        conn.close()

@lider.route('/obtener_perfil_lider')
@lider_required
def obtener_perfil_lider():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row

    usuario_id = session.get('usuario_id')
    usuario_sesion = session.get('usuario')

    if isinstance(usuario_sesion, dict):
        nombre_usuario = usuario_sesion.get('nombre_usuario')
    else:
        nombre_usuario = usuario_sesion

    user = conn.execute('SELECT * FROM Usuario WHERE id = ?', (usuario_id,)).fetchone()
    conn.close()

    if user:
        return jsonify({
            'success': True, 
            'nombre': user['nombre_completo'], 
            'correo': user['correo'],
            'telefono': user['telefono'] or '',
            'direccion': user['direccion'] or '',
            'descripcion': user['descripcion'] or ''
        })
    else:
        return jsonify({'success': False, 'message': 'Usuario no encontrado'})

@lider.route('/actualizar_perfil_lider', methods=['POST'])
@lider_required
def actualizar_perfil_lider():
    if 'usuario_id' not in session:
        return jsonify({'success': False, 'message': 'Sesión expirada'})

    usuario_id = session.get('usuario_id')
    usuario_sesion = session.get('usuario')

    nombre = request.form['nombre']
    correo = request.form['correo']
    telefono = request.form.get('telefono', '')
    direccion = request.form.get('direccion', '')
    descripcion = request.form.get('descripcion', '')
    contraseña_actual = request.form.get('contraseña_actual', '')
    nueva_contraseña = request.form.get('nueva_contraseña', '')
    confirmar_contraseña = request.form.get('confirmar_contraseña', '')

    nueva_foto = request.files.get('imagen')
    nombre_foto = None

    if nueva_foto and nueva_foto.filename != '':
        nombre_archivo = secure_filename(nueva_foto.filename)
        ruta_archivo = os.path.join('static', 'avatars', nombre_archivo)
        nueva_foto.save(ruta_archivo)
        nombre_foto = nombre_archivo

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    user = cursor.execute('SELECT * FROM Usuario WHERE id = ?', (usuario_id,)).fetchone()
    if not user:
        conn.close()
        return jsonify({'success': False, 'message': 'Usuario no encontrado'})

    if contraseña_actual and nueva_contraseña and confirmar_contraseña:
        if nueva_contraseña != confirmar_contraseña:
            conn.close()
            return jsonify({'success': False, 'message': 'Las contraseñas nuevas no coinciden'})
        if not check_password_hash(user['contraseña'], contraseña_actual):
            conn.close()
            return jsonify({'success': False, 'message': 'La contraseña actual es incorrecta'})
        nueva_contraseña_hash = generate_password_hash(nueva_contraseña)
    else:
        nueva_contraseña_hash = user['contraseña']

    # 🔥 Actualizar perfil con o sin imagen
    if nombre_foto:
        cursor.execute('''
            UPDATE Usuario 
            SET nombre_completo = ?, correo = ?, telefono = ?, direccion = ?, descripcion = ?, contraseña = ?, foto = ?
            WHERE id = ?
        ''', (nombre, correo, telefono, direccion, descripcion, nueva_contraseña_hash, nombre_foto, usuario_id))
    else:
        cursor.execute('''
            UPDATE Usuario 
            SET nombre_completo = ?, correo = ?, telefono = ?, direccion = ?, descripcion = ?, contraseña = ?
            WHERE id = ?
        ''', (nombre, correo, telefono, direccion, descripcion, nueva_contraseña_hash, usuario_id))

    conn.commit()
    conn.close()

    return jsonify({'success': True, 'message': 'Perfil actualizado correctamente'})

from datetime import datetime

@lider.route('/calendario')
def calendario():
    mes = request.args.get('mes', datetime.now().month)
    anio = request.args.get('anio', datetime.now().year)

    conexion = sqlite3.connect('gestor_de_tareas.db')
    conexion.row_factory = sqlite3.Row
    cursor = conexion.cursor()

    cursor.execute('''
        SELECT id, titulo, descripcion, fecha_vencimiento, prioridad, estado
        FROM tareas
        WHERE strftime('%m', fecha_vencimiento) = ? AND strftime('%Y', fecha_vencimiento) = ?
    ''', (f'{int(mes):02d}', str(anio)))

    tareas = [dict(fila) for fila in cursor.fetchall()]
    conexion.close()

    return render_template('lider.html', tareas=tareas, mes=mes, anio=anio)


@lider.route('/descargar_informe')
def descargar_informe():
    if 'usuario' not in session:
        return redirect(url_for('login.login'))

    grupo = session.get('grupo')
    hoy = datetime.now()
    primer_dia = f"{hoy.year}-{hoy.month:02}-01"
    siguiente_mes = f"{hoy.year + 1}-01-01" if hoy.month == 12 else f"{hoy.year}-{hoy.month + 1:02}-01"

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.titulo, t.descripcion, t.fecha_registro, t.fecha_vencimiento, t.estado, 
               COALESCE(p.nombre, 'Proyecto no especificado') AS proyecto
        FROM tareas t
        LEFT JOIN Proyecto p ON t.id_proyecto = p.id
        WHERE LOWER(t.curso_destino) = LOWER(?) 
          AND t.fecha_vencimiento >= ? AND t.fecha_vencimiento < ?
    """, (grupo, primer_dia, siguiente_mes))

    tareas = cursor.fetchall()
    conn.close()

    nombre_proyecto = tareas[0]['proyecto'] if tareas else 'Proyecto no especificado'

    pdf = FPDF()
    pdf.add_page()

    # 🎨 Fondo
    pdf.set_fill_color(230, 240, 255)
    pdf.rect(0, 0, 210, 297, 'F')

    # 🖼️ Logo
    try:
        pdf.image('static/avatars/barra_lateral.png', x=10, y=8, w=30)
    except:
        pass

    # 📄 Encabezado
    pdf.set_font('Arial', 'B', 16)
    pdf.ln(10)
    pdf.cell(0, 10, 'Informe de Tareas', ln=True, align='C')
    pdf.ln(5)

    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Grupo: {grupo}', ln=True, align='C')
    pdf.cell(0, 10, f'Proyecto: {nombre_proyecto}', ln=True, align='C')
    pdf.cell(0, 10, f'Mes: {hoy.strftime("%B %Y")}', ln=True, align='C')
    pdf.ln(10)

    if tareas:
        # 🧮 Ancho total de la tabla y márgenes para centrar
        ancho_total = 40 + 70 + 30 + 30 + 30  # suma de anchos de columnas
        margen_izquierdo = (210 - ancho_total) / 2
        pdf.set_x(margen_izquierdo)

        # Cabecera
        pdf.set_fill_color(180, 210, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(40, 10, 'Título', 1, 0, 'C', 1)
        pdf.cell(70, 10, 'Descripción', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Fecha Reg.', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Fecha Entrega', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Estado', 1, 1, 'C', 1)

        pdf.set_font('Arial', '', 10)
        line_height = 6

        for tarea in tareas:
            # Altura dinámica: calculamos cuál celda es más alta (título o descripción)
            temp_pdf = FPDF()
            temp_pdf.add_page()
            temp_pdf.set_font('Arial', '', 10)
            temp_pdf.set_xy(0, 0)
            temp_pdf.multi_cell(40, line_height, tarea["titulo"])
            h_titulo = temp_pdf.get_y()
            temp_pdf.set_xy(0, 0)
            temp_pdf.multi_cell(70, line_height, tarea["descripcion"])
            h_desc = temp_pdf.get_y()
            altura = max(h_titulo, h_desc)

            # Comenzar desde el margen izquierdo centrado
            pdf.set_x(margen_izquierdo)
            x = pdf.get_x()
            y = pdf.get_y()

            # Título
            pdf.multi_cell(40, line_height, tarea["titulo"], border=1, align='C')
            x += 40
            pdf.set_xy(x, y)

            # Descripción
            pdf.multi_cell(70, line_height, tarea["descripcion"], border=1, align='L')
            x += 70
            pdf.set_xy(x, y)

            # Fechas y estado en celdas normales con misma altura
            pdf.cell(30, altura, tarea["fecha_registro"] or 'N/A', border=1, align='C')
            pdf.cell(30, altura, tarea["fecha_vencimiento"], border=1, align='C')
            pdf.cell(30, altura, tarea["estado"], border=1, align='C')
            pdf.ln(altura)
    else:
        pdf.cell(0, 10, 'No hay tareas asignadas este mes.', ln=True, align='C')

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output = BytesIO(pdf_bytes)

    return send_file(pdf_output, as_attachment=True, download_name='informe_proyecto.pdf', mimetype='application/pdf')
