from flask import Blueprint, jsonify, request,render_template,send_file,session, current_app
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from fpdf import FPDF
from unidecode import unidecode
from datetime import datetime
import sqlite3
import os
from app.session_decorators import api_admin_required, nocache

api_blueprint = Blueprint('api', __name__)

#Esto permite que SQLite espere unos segundos antes de lanzar el error de "locked":
def get_db_connection():
    conn = sqlite3.connect('gestor_de_tareas.db', timeout=10)
    conn.row_factory = sqlite3.Row
    return conn

# --- Crea usuarios de prueba si no existen ---
def crear_usuarios_prueba():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Verifica si hay usuarios
    cursor.execute('SELECT COUNT(*) FROM Usuario')
    total = cursor.fetchone()[0]

    if total == 0:
        cursor.execute('''
            INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("Pedro Lider", "pedro_l", "1111", "pedro@example.com", "1234", "lider", "activo"))

        cursor.execute('''
            INSERT INTO Usuario (nombre_completo, nombre_usuario, documento, correo, contraseña, rol, estado)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', ("Marta Trabajadora", "marta_t", "2222", "marta@example.com", "1234", "trabajador", "activo"))

        conn.commit()

    conn.close()

# Ejecutar una vez al importar este archivo
crear_usuarios_prueba()

#--- Configuracion de rutas para imagenes de chat --
RUTA_IMAGENES_CHAT = 'static/chat_images'

# Asegurar que exista la carpeta para imágenes de chat
if not os.path.exists(RUTA_IMAGENES_CHAT):
    os.makedirs(RUTA_IMAGENES_CHAT)

#Contador de lideres activos
@api_blueprint.route('/api/lider/count')
@api_admin_required
def api_lider_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE rol="lider" AND estado="activo"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

#Contador de trabajadores activos
@api_blueprint.route('/api/trabajadores/count')
@api_admin_required
def api_trabajadores_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE estado="activo" AND rol="trabajador"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

#Contador de proyectos activos
@api_blueprint.route('/api/proyectos/count')
@api_admin_required
def contar_proyectos_activos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Proyecto WHERE estado = 'activo'")
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify({'count': count})


# 1. Ruta para registrar un lider
@api_blueprint.route('/api/lideres/crear', methods=['POST'])
@api_admin_required
def registrar_lider():
    data = request.get_json()

    nombre = data.get('nombre')
    apellido = data.get('apellido')
    usuario = data.get('usuario')
    contrasena = data.get('contrasena')
    documento = data.get('documento')
    grupo = data.get('grupo')
    proyecto = data.get('proyecto')
    correo = data.get('correo')
    telefono = data.get('telefono')
    direccion = data.get('direccion')

    nombre_completo = f"{nombre} {apellido}"
    contrasena_hash = generate_password_hash(contrasena)

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            # Verificar si el usuario ya existe
            existe = cursor.execute("SELECT id FROM Usuario WHERE nombre_usuario = ?", (usuario,)).fetchone()
            if existe:
                return jsonify({"error": "El nombre de usuario ya está en uso"}), 400

            # Insertar nuevo líder
            cursor.execute('''
                INSERT INTO Usuario (
                    nombre_completo,
                    nombre_usuario,
                    documento,
                    correo,
                    contraseña,
                    rol,
                    estado,
                    grupo,
                    proyecto,
                    telefono,
                    direccion
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                nombre_completo,
                usuario,
                documento,
                correo,
                contrasena_hash,
                'lider',
                'activo',
                grupo,
                proyecto,
                telefono,
                direccion
            ))

            conn.commit()

        return jsonify({"message": "Líder registrado exitosamente"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    
# 2. Ruta para inactivar líder
@api_blueprint.route('/api/lider/inactivar/<int:id>', methods=['POST'])
@api_admin_required
def inactivar_lider(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Líder inactivado"}), 200

# 3. Ruta para obtener los datos de un líder específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/lider/<int:id>')
@api_admin_required
def obtener_lider(id):
    with get_db_connection() as conn:
        lider = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'lider'", (id,)).fetchone()

    if lider:
        return jsonify(dict(lider))
    else:
        return jsonify({"error": "Líder no encontrado"}), 404

# 4. Ruta para actualizar un lider
@api_blueprint.route('/api/lider/actualizar', methods=['POST'])
@api_admin_required
def actualizar_lider():
    data = request.get_json()
    id = data.get('id')

    campos = ['nombre_completo', 'nombre_usuario', 'documento', 'correo', 'grupo', 'proyecto', 'telefono', 'direccion']
    valores = [data.get(c) for c in campos]

    with get_db_connection() as conn:
        conn.execute(f'''
            UPDATE Usuario SET
                nombre_completo = ?,
                nombre_usuario = ?,
                documento = ?,
                correo = ?,
                grupo = ?,
                proyecto = ?,
                telefono = ?,
                direccion = ?
            WHERE id = ? AND rol = 'lider'
        ''', (*valores, id))
        conn.commit()

    return jsonify({"message": "Líder actualizado correctamente"})

# 5. Ruta para obtener todos los líderes activos
@api_blueprint.route('/api/lideres')
@api_admin_required
def obtener_lideres():
    with get_db_connection() as conn:
        lideres = conn.execute("SELECT * FROM Usuario WHERE rol = 'lider' AND estado = 'activo'").fetchall()
    return jsonify([dict(l) for l in lideres])

# 6.Ruta para obtener todos los trabajadores activos
@api_blueprint.route('/api/trabajadores')
@api_admin_required
def obtener_trabajadores():
    with get_db_connection() as conn:
        trabajadores = conn.execute("SELECT * FROM Usuario WHERE rol = 'trabajador' AND estado = 'activo'").fetchall()
    return jsonify([dict(t) for t in trabajadores])


# 7. Ruta para inactivar trabahajadores
@api_blueprint.route('/api/trabajador/inactivar/<int:id>', methods=['POST'])
@api_admin_required
def inactivar_trabajador(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Trabajador inactivado"}), 200

# 8. Ruta para obtener los datos de un trabajador específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/trabajador/<int:id>')
@api_admin_required
def obtener_trabajador(id):
    with get_db_connection() as conn:
        trabajador = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'trabajador' AND estado = 'activo'", (id,)).fetchone()

    if trabajador:
        return jsonify(dict(trabajador))
    else:
        return jsonify({"error": "Trabajador no encontrado o inactivo"}), 404


# 9. Ruta para actualizar un trabajador
@api_blueprint.route('/api/trabajador/actualizar', methods=['POST'])
@api_admin_required
def actualizar_trabajador():
    data = request.get_json()
    id = data.get('id')

    campos = ['nombre_completo', 'nombre_usuario', 'documento', 'correo', 'grupo', 'proyecto', 'telefono', 'direccion']
    valores = [data.get(c) for c in campos]

    with get_db_connection() as conn:
        conn.execute('''
            UPDATE Usuario SET
                nombre_completo = ?,
                nombre_usuario = ?,
                documento = ?,
                correo = ?,
                grupo = ?,
                proyecto = ?,
                telefono = ?,
                direccion = ?
            WHERE id = ? AND rol = 'trabajador'
        ''', (*valores, id))
        conn.commit()

    return jsonify({"message": "Trabajador actualizado correctamente"})

# 10.  Ruta para actualizar el perfil del administrador
@api_blueprint.route('/perfil/actualizar', methods=['POST'])
@api_admin_required
def actualizar_perfil():
    nombre = request.form.get('nombre') or session.get('nombre')
    descripcion = request.form.get('descripcion') or session.get('descripcion')
    imagen = request.files.get('imagen')

    ruta_final = session.get('avatar', '/static/avatars/perfil.jpeg')  # Valor por defecto

    if imagen:
        # Guardar siempre como perfil.jpeg
        ruta = os.path.join('static/avatars', 'perfil.jpeg')
        imagen.save(ruta)
        ruta_final = '/static/avatars/perfil.jpeg'

    # Guardar datos en sesión para mantenerlos disponibles
    session['nombre'] = nombre
    session['descripcion'] = descripcion
    session['avatar'] = ruta_final

    return jsonify({
        'nombre': nombre,
        'descripcion': descripcion,
        'imagen': ruta_final
    })

#11. Ruta para crear un proyecto
# Crear proyecto
@api_blueprint.route('/api/proyecto/crear', methods=['POST'])
@api_admin_required
def crear_proyecto():
    data = request.get_json()
    nombre = data.get('nombre')
    descripcion = data.get('descripcion')
    fecha_inicio = data.get('fecha_inicio')
    fecha_fin = data.get('fecha_fin')
    grupo = data.get('grupo')

    if not all([nombre, descripcion, fecha_inicio, fecha_fin, grupo]):
        return jsonify({'error': 'Faltan campos'}), 400

    conn = get_db_connection()
    cursor = conn.cursor()

    # Verificar si ya existe un proyecto con ese nombre
    cursor.execute("SELECT id FROM Proyecto WHERE nombre = ? AND estado = 'activo'", (nombre,))
    existente = cursor.fetchone()
    if existente:
        conn.close()
        return jsonify({'error': f'El proyecto "{nombre}" ya existe'}), 400

    # Insertar si no existe
    cursor.execute("""
        INSERT INTO Proyecto (nombre, descripcion, fecha_inicio, fecha_fin, grupo, estado)
        VALUES (?, ?, ?, ?, ?, 'activo')
    """, (nombre, descripcion, fecha_inicio, fecha_fin, grupo))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Proyecto creado exitosamente'})

# Obtener proyectos activos
@api_blueprint.route('/api/proyectos', methods=['GET'])
@api_admin_required
def obtener_proyectos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, nombre, descripcion, fecha_inicio, fecha_fin, grupo, estado
        FROM Proyecto
        WHERE estado = 'activo'
    """)
    proyectos = cursor.fetchall()
    conn.close()

    resultado = [
        {
            'id': p['id'],
            'nombre': p['nombre'],
            'descripcion': p['descripcion'],
            'fecha_inicio': p['fecha_inicio'],
            'fecha_fin': p['fecha_fin'],
            'grupo': p['grupo'],
            'estado': p['estado']
        }
        for p in proyectos
    ]
    return jsonify(resultado)

# Inactivar proyecto
@api_blueprint.route('/api/proyecto/inactivar/<int:id>', methods=['POST'])
@api_admin_required
def inactivar_proyecto(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Proyecto SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Proyecto inactivado correctamente"})

#Editar proyecto
@api_blueprint.route('/api/proyecto/editar/<int:id>', methods=['POST'])
@api_admin_required
def editar_proyecto(id):
    data = request.get_json()
    with get_db_connection() as conn:
        conn.execute('''
            UPDATE Proyecto SET nombre = ?, descripcion = ?, fecha_inicio = ?, fecha_fin = ?, grupo = ?
            WHERE id = ?
        ''', (data['nombre'], data['descripcion'], data['fecha_inicio'], data['fecha_fin'], data['grupo'], id))
        conn.commit()
    return jsonify({'message': 'Proyecto actualizado exitosamente'})

#Obtener proyecto por ID
@api_blueprint.route('/api/proyecto/<int:id>', methods=['GET'])
@api_admin_required
def obtener_proyecto_por_id(id):
    with get_db_connection() as conn:
        proyecto = conn.execute('SELECT * FROM Proyecto WHERE id = ?', (id,)).fetchone()
        if proyecto:
            return jsonify(dict(proyecto))
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
#Parte de Asignacion
# 1. Ruta para obtener trabajadores sin grupo asignado
@api_blueprint.route('/api/trabajadores/sin_grupo')
@api_admin_required
def trabajadores_sin_grupo():
    with get_db_connection() as conn:
        trabajadores = conn.execute("""
            SELECT id, nombre_completo FROM Usuario
            WHERE rol = 'trabajador' AND estado = 'activo' AND (grupo IS NULL OR grupo = '')
        """).fetchall()
    return jsonify([dict(t) for t in trabajadores])

# 2. Ruta para asignar grupo a trabajador y actualizar proyecto automáticamente
@api_blueprint.route('/api/asignar_grupo', methods=['POST'])
@api_admin_required
def asignar_grupo_a_trabajador():
    data = request.get_json()
    trabajador_id = data.get('id')
    grupo = data.get('grupo')

    if not grupo:
        return jsonify({'status': 'error', 'message': 'Grupo requerido'}), 400

    with get_db_connection() as conn:
        # Verificar si el grupo está asociado a un proyecto activo
        proyecto = conn.execute("""
            SELECT nombre FROM Proyecto
            WHERE grupo = ? AND estado = 'activo'
        """, (grupo,)).fetchone()

        if not proyecto:
            return jsonify({'status': 'error', 'message': 'No hay proyecto activo para este grupo'}), 400

        # Actualizar grupo y proyecto en el trabajador
        conn.execute("""
            UPDATE Usuario
            SET grupo = ?, proyecto = ?
            WHERE id = ? AND rol = 'trabajador'
        """, (grupo, proyecto['nombre'], trabajador_id))

        conn.commit()

    return jsonify({'status': 'success'})

#Parte de seguimiento de proyectos
@api_blueprint.route('/api/proyecto/<nombre>', methods=['GET'])
@api_admin_required
def seguimiento_proyecto(nombre):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Total tareas del proyecto
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ?", (nombre,))
    total = cursor.fetchone()[0]

    # Tareas completadas
    cursor.execute("SELECT COUNT(*) FROM tareas WHERE id_proyecto = ? AND estado = 'enviada'", (nombre,))
    completadas = cursor.fetchone()[0]

    # Tareas pendientes con nombre del trabajador
    cursor.execute("""
        SELECT t.titulo, t.fecha_vencimiento, u.nombre_completo
        FROM tareas t
        JOIN Usuario u ON t.id_usuario_asignado = u.id
        WHERE t.id_proyecto = ? AND t.estado = 'pendiente'
    """, (nombre,))
    pendientes = cursor.fetchall()

    conn.close()

    return jsonify({
        "tareas_total": total,
        "tareas_completadas": completadas,
        "trabajadores_con_tareas_pendientes": [dict(p) for p in pendientes]
    })

@api_blueprint.route('/api/proyecto/<nombre>/pdf', methods=['GET'])
@api_admin_required
def generar_pdf_proyecto(nombre):
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.titulo, t.fecha_vencimiento, u.nombre_completo
        FROM tareas t
        JOIN Usuario u ON t.id_usuario_asignado = u.id
        WHERE t.id_proyecto = ? AND t.estado = 'pendiente'
    """, (nombre,))
    tareas = cursor.fetchall()
    conn.close()

    # Crear PDF
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Tareas pendientes del proyecto: {unidecode(nombre)}", ln=True)

    pdf.set_font("Arial", "", 12)
    for t in tareas:
        pdf.cell(0, 10, f"Título: {t['titulo']}", ln=True)
        pdf.cell(0, 10, f"Trabajador: {t['nombre_completo']}", ln=True)
        pdf.cell(0, 10, f"Fecha de vencimiento: {t['fecha_vencimiento']}", ln=True)
        pdf.ln(5)

    ruta = f"static/pdf/pendientes_{unidecode(nombre).replace(' ', '_')}.pdf"
    os.makedirs("static/pdf", exist_ok=True)
    pdf.output(ruta)

    return send_file(ruta, as_attachment=True)

# Ruta para obtener informacion del progreso de los proyectos
@api_blueprint.route('/api/proyecto/<nombre>', methods=['GET'])
@api_admin_required
def obtener_progreso_proyecto(nombre):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Obtener grupo del proyecto
    cursor.execute("SELECT grupo FROM Proyecto WHERE nombre = ?", (nombre,))
    proyecto = cursor.fetchone()
    if not proyecto:
        return jsonify({"error": "Proyecto no encontrado"}), 404

    grupo = proyecto['grupo']

    # Obtener todos los trabajadores del grupo
    cursor.execute("SELECT id, nombre || ' ' || apellido AS nombre_completo FROM Usuario WHERE grupo = ? AND rol = 'trabajador'", (grupo,))
    trabajadores = cursor.fetchall()
    trabajadores_dict = {t['id']: t['nombre_completo'] for t in trabajadores}
    trabajador_ids = list(trabajadores_dict.keys())

    # Obtener tareas del grupo
    cursor.execute("SELECT id, titulo, fecha_vencimiento, estado FROM tareas WHERE curso_del_grupo = ?", (grupo,))
    tareas = cursor.fetchall()

    total_tareas = len(tareas)
    tareas_pendientes = []
    completadas = 0

    for tarea in tareas:
        if tarea['estado'] == 'completado':
            completadas += 1
            continue

        tarea_id = tarea['id']

        # Buscar qué usuarios entregaron esta tarea
        cursor.execute("SELECT DISTINCT usuario_id FROM tarea_archivos WHERE tarea_id = ?", (tarea_id,))
        entregas = {row['usuario_id'] for row in cursor.fetchall()}

        # Trabajadores que aún no han entregado
        no_entregaron = [trabajadores_dict[uid] for uid in trabajador_ids if uid not in entregas]

        tareas_pendientes.append({
            "titulo": tarea['titulo'],
            "fecha_vencimiento": tarea['fecha_vencimiento'] or "Sin fecha",
            "no_entregaron": no_entregaron
        })

    porcentaje = round((completadas / total_tareas) * 100, 2) if total_tareas > 0 else 0

    conn.close()

    return jsonify({
        "progreso": porcentaje,
        "pendientes": tareas_pendientes
    })
#Ruta de chatbox
@api_blueprint.route('/api/usuarios/chat')
def obtener_usuarios_para_chat():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify([])

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Mostrar solo líderes activos para el trabajador
    cursor.execute('''
        SELECT id, nombre_completo, rol, foto
        FROM Usuario
        WHERE estado = 'activo' AND id != ? AND rol = 'lider'
        ORDER BY nombre_completo
    ''', (usuario_id,))

    usuarios = cursor.fetchall()
    conn.close()
    return jsonify([dict(u) for u in usuarios])



# Ruta para que el líder vea mensajes con un trabajador específico
@api_blueprint.route('/api/chat/<int:receptor_id>')
def obtener_mensajes_chat_lider(receptor_id):
    emisor_id = session.get('usuario_id')
    if not emisor_id:
        return jsonify([])
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT m.*, u.nombre_completo as emisor_nombre, u.rol as emisor_rol
        FROM mensajes m
        JOIN Usuario u ON m.emisor_id = u.id
        WHERE (m.emisor_id = ? AND m.receptor_id = ?)
           OR (m.emisor_id = ? AND m.receptor_id = ?)
        ORDER BY m.fecha ASC
    ''', (emisor_id, receptor_id, receptor_id, emisor_id))
    mensajes = cursor.fetchall()
    conn.close()
    return jsonify([dict(m) for m in mensajes])
@api_blueprint.route('/api/chat/trabajadores')
def obtener_trabajadores_con_chat():
    """Devuelve la lista de trabajadores para líderes (solo del mismo grupo)"""
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify([])
    
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Obtener el rol y grupo del usuario actual
    cursor.execute('SELECT rol, grupo FROM Usuario WHERE id = ?', (usuario_id,))
    usuario_actual = cursor.fetchone()
    
    if not usuario_actual:
        conn.close()
        return jsonify([])
    
    if usuario_actual['rol'] == 'lider':
        # Líderes solo ven trabajadores de su mismo grupo
        cursor.execute('''
            SELECT DISTINCT u.id, u.nombre_completo, u.foto
            FROM Usuario u
            WHERE u.rol = 'trabajador' 
            AND u.estado = 'activo'
            AND u.grupo = ?
            ORDER BY u.nombre_completo
        ''', (usuario_actual['grupo'],))
    else:
        # Por si acaso, devolver lista vacía para otros roles
        conn.close()
        return jsonify([])
    
    trabajadores = cursor.fetchall()
    conn.close()
    
    return jsonify([dict(t) for t in trabajadores])


@api_blueprint.route('/api/chat/enviar', methods=['POST'])
def enviar_mensaje_texto():
    data = request.get_json()
    emisor_id = session.get('usuario_id')
    receptor_id = data.get('receptor_id')
    mensaje = data.get('mensaje')

    if not emisor_id or not receptor_id or not mensaje:
        return jsonify({'error': 'Datos incompletos'}), 400

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre_completo FROM Usuario WHERE id = ?', (emisor_id,))
    emisor_nombre = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO mensajes (emisor_id, emisor, receptor_id, mensaje, tipo)
        VALUES (?, ?, ?, ?, 'texto')
    ''', (emisor_id, emisor_nombre, receptor_id, mensaje))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})


@api_blueprint.route('/api/chat/enviar-imagen', methods=['POST'])
def enviar_imagen():
    emisor_id = session.get('usuario_id')
    receptor_id = request.form.get('receptor_id')
    imagen = request.files.get('imagen')

    if not emisor_id or not receptor_id or not imagen:
        return jsonify({'error': 'Datos faltantes'}), 400

    nombre_seguro = secure_filename(imagen.filename)
    ruta_archivo = os.path.join(RUTA_IMAGENES_CHAT, nombre_seguro)
    imagen.save(ruta_archivo)
    url_imagen = f'/{ruta_archivo}'

    conn = sqlite3.connect('gestor_de_tareas.db')
    cursor = conn.cursor()
    cursor.execute('SELECT nombre_completo FROM Usuario WHERE id = ?', (emisor_id,))
    emisor_nombre = cursor.fetchone()[0]

    cursor.execute('''
        INSERT INTO mensajes (emisor_id, emisor, receptor_id, tipo, imagen_url)
        VALUES (?, ?, ?, 'imagen', ?)
    ''', (emisor_id, emisor_nombre, receptor_id, url_imagen))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@api_blueprint.route('/api/lideres/chat', methods=['GET'])
def obtener_lideres_para_chat():
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return jsonify([])

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, nombre_completo, foto 
        FROM Usuario 
        WHERE rol = 'lider' AND estado = 'activo' AND id != ?
    ''', (usuario_id,))
    lideres = cursor.fetchall()
    conn.close()

    return jsonify([dict(l) for l in lideres])

@api_blueprint.route('/api/administrador/chat')
def obtener_info_admin_para_lider():
    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, nombre_completo, foto FROM Usuario WHERE rol = 'admin' LIMIT 1")
    admin = cursor.fetchone()
    conn.close()
    return jsonify(dict(admin) if admin else {})

#Ruta para descargar informe general de tareas
@api_blueprint.route('/descargar_informe')
@api_admin_required
def descargar_informe_admin():
    from fpdf import FPDF
    from io import BytesIO
    from datetime import datetime
    import sqlite3

    # Parámetros de mes y año
    mes = request.args.get('mes')
    hoy = datetime.now()
    anio = hoy.year
    if mes is None:
        mes = f"{hoy.month:02}"
    else:
        mes = str(mes).zfill(2)
    # Primer y último día del mes
    primer_dia = f"{anio}-{mes}-01"
    if mes == '12':
        siguiente_mes = f"{anio + 1}-01-01"
    else:
        siguiente_mes = f"{anio}-{int(mes)+1:02}-01"

    conn = sqlite3.connect('gestor_de_tareas.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("""
        SELECT t.titulo, t.descripcion, t.fecha_registro, t.fecha_vencimiento, t.estado, \
               COALESCE(p.nombre, 'Proyecto no especificado') AS proyecto, t.curso_destino
        FROM tareas t
        LEFT JOIN Proyecto p ON t.id_proyecto = p.id
        WHERE t.fecha_vencimiento >= ? AND t.fecha_vencimiento < ?
    """, (primer_dia, siguiente_mes))

    tareas = cursor.fetchall()
    conn.close()

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
    pdf.cell(0, 10, 'Informe General de Tareas', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 10, f'Mes: {datetime.strptime(mes, "%m").strftime("%B")} {anio}', ln=True, align='C')
    pdf.ln(10)

    if tareas:
        ancho_total = 30 + 40 + 30 + 30 + 30 + 40  # Proyecto, Título, Fechas, Estado, Grupo
        margen_izquierdo = (210 - ancho_total) / 2
        pdf.set_x(margen_izquierdo)
        pdf.set_fill_color(180, 210, 255)
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(30, 10, 'Proyecto', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Título', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Fecha Reg.', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Fecha Entrega', 1, 0, 'C', 1)
        pdf.cell(30, 10, 'Estado', 1, 0, 'C', 1)
        pdf.cell(40, 10, 'Grupo', 1, 1, 'C', 1)
        pdf.set_font('Arial', '', 10)
        line_height = 6
        for tarea in tareas:
            pdf.set_x(margen_izquierdo)
            pdf.cell(30, line_height, tarea['proyecto'], border=1, align='C')
            pdf.cell(40, line_height, tarea['titulo'], border=1, align='C')
            pdf.cell(30, line_height, tarea['fecha_registro'] or 'N/A', border=1, align='C')
            pdf.cell(30, line_height, tarea['fecha_vencimiento'], border=1, align='C')
            pdf.cell(30, line_height, tarea['estado'], border=1, align='C')
            pdf.cell(40, line_height, tarea['curso_destino'], border=1, align='C')
            pdf.ln(line_height)
    else:
        pdf.cell(0, 10, 'No hay tareas registradas este mes.', ln=True, align='C')

    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    pdf_output = BytesIO(pdf_bytes)

    return send_file(pdf_output, as_attachment=True, download_name='informe_general.pdf', mimetype='application/pdf')
