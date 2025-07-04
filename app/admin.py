from flask import Blueprint, jsonify, request,render_template,send_file,session
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from fpdf import FPDF
from unidecode import unidecode
from datetime import datetime
import sqlite3
import os

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

#Contador de lideres activos
@api_blueprint.route('/api/lider/count')
def api_lider_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE rol="lider" AND estado="activo"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

#Contador de trabajadores activos
@api_blueprint.route('/api/trabajadores/count')
def api_trabajadores_count():
    conn = get_db_connection()
    cnt = conn.execute('SELECT COUNT(*) FROM Usuario WHERE estado="activo" AND rol="trabajador"').fetchone()[0]
    conn.close()
    return jsonify(count=cnt)

#Contador de proyectos activos
@api_blueprint.route('/api/proyectos/count')
def contar_proyectos_activos():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM Proyecto WHERE estado = 'activo'")
    count = cursor.fetchone()[0]
    conn.close()
    return jsonify({'count': count})


# 1. Ruta para registrar un lider
@api_blueprint.route('/api/lideres/crear', methods=['POST'])
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
def inactivar_lider(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Líder inactivado"}), 200

# 3. Ruta para obtener los datos de un líder específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/lider/<int:id>')
def obtener_lider(id):
    with get_db_connection() as conn:
        lider = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'lider'", (id,)).fetchone()

    if lider:
        return jsonify(dict(lider))
    else:
        return jsonify({"error": "Líder no encontrado"}), 404

# 4. Ruta para actualizar un lider
@api_blueprint.route('/api/lider/actualizar', methods=['POST'])
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
def obtener_lideres():
    with get_db_connection() as conn:
        lideres = conn.execute("SELECT * FROM Usuario WHERE rol = 'lider' AND estado = 'activo'").fetchall()
    return jsonify([dict(l) for l in lideres])

# 6.Ruta para obtener todos los trabajadores activos
@api_blueprint.route('/api/trabajadores')
def obtener_trabajadores():
    with get_db_connection() as conn:
        trabajadores = conn.execute("SELECT * FROM Usuario WHERE rol = 'trabajador' AND estado = 'activo'").fetchall()
    return jsonify([dict(t) for t in trabajadores])


# 7. Ruta para inactivar trabahadores
@api_blueprint.route('/api/trabajador/inactivar/<int:id>', methods=['POST'])
def inactivar_trabajador(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Usuario SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Trabajador inactivado"}), 200

# 8. Ruta para obtener los datos de un trabajador específico (por ID), usada para cargar el formulario de edición
@api_blueprint.route('/api/trabajador/<int:id>')
def obtener_trabajador(id):
    with get_db_connection() as conn:
        trabajador = conn.execute("SELECT * FROM Usuario WHERE id = ? AND rol = 'trabajador' AND estado = 'activo'", (id,)).fetchone()

    if trabajador:
        return jsonify(dict(trabajador))
    else:
        return jsonify({"error": "Trabajador no encontrado o inactivo"}), 404


# 9. Ruta para actualizar un trabajador
@api_blueprint.route('/api/trabajador/actualizar', methods=['POST'])
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
def inactivar_proyecto(id):
    with get_db_connection() as conn:
        conn.execute("UPDATE Proyecto SET estado = 'inactivo' WHERE id = ?", (id,))
        conn.commit()
    return jsonify({"message": "Proyecto inactivado correctamente"})

#Editar proyecto
@api_blueprint.route('/api/proyecto/editar/<int:id>', methods=['POST'])
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
def obtener_proyecto_por_id(id):
    with get_db_connection() as conn:
        proyecto = conn.execute('SELECT * FROM Proyecto WHERE id = ?', (id,)).fetchone()
        if proyecto:
            return jsonify(dict(proyecto))
        return jsonify({'error': 'Proyecto no encontrado'}), 404
    
#Parte de Asignacion
# 1. Ruta para obtener trabajadores sin grupo asignado
@api_blueprint.route('/api/trabajadores/sin_grupo')
def trabajadores_sin_grupo():
    with get_db_connection() as conn:
        trabajadores = conn.execute("""
            SELECT id, nombre_completo FROM Usuario
            WHERE rol = 'trabajador' AND estado = 'activo' AND (grupo IS NULL OR grupo = '')
        """).fetchall()
    return jsonify([dict(t) for t in trabajadores])

# 2. Ruta para asignar grupo a trabajador y actualizar proyecto automáticamente
@api_blueprint.route('/api/asignar_grupo', methods=['POST'])
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
