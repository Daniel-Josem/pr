// --- SOCKET.IO para mensajes en tiempo real ---
if (typeof io !== 'undefined') {
  const socket = io();
  
  // Escuchar nuevos mensajes
  socket.on('nuevo_mensaje', function(msg) {
    // Si el chat popup está abierto y es el chat correcto, mostrar el mensaje
    if (usuarioChatActual && msg.emisor_id == usuarioChatActual) {
      agregarMensajeAlPopup(msg);
    }
    // También actualizar la lista de chats para mostrar badge/notificación
    cargarListaChats();
  });
  
  // Hacer el socket disponible globalmente
  window.socket = socket;
}

function agregarMensajeAlPopup(m) {
  const contenedor = document.getElementById('chat-popup-mensajes');
  const div = document.createElement('div');
  div.classList.add('chat-bubble');
  if (m.tipo === 'imagen') {
    const img = document.createElement('img');
    img.src = m.imagen_url;
    img.classList.add('chat-img-click');
    img.onclick = () => mostrarImagenGrande(img.src);
    div.innerHTML = '';
    div.appendChild(img);
  } else {
    div.textContent = `${m.emisor_nombre || m.emisor} (${m.emisor_rol || ''}): ${m.mensaje}`;
  }
  contenedor.appendChild(div);
  contenedor.scrollTop = contenedor.scrollHeight;
}
document.addEventListener('DOMContentLoaded', function () {
    // Event listeners para formularios de tareas
    document.getElementById('btnCrearTarea').addEventListener('click', () => {
        document.getElementById('formEditar').reset();
        document.getElementById('tareaId').value = '';
        document.getElementById('nombreArchivoActual').textContent = '';
        document.getElementById('formEditar').action = '/crear_tarea';
    });

    // Script para cargar datos al editar
    document.querySelectorAll('.btnEditar').forEach(button => {
        button.addEventListener('click', () => {
            document.getElementById('formEditar').reset();
            document.getElementById('tareaId').value = button.getAttribute('data-id');
            document.getElementById('titulo').value = button.getAttribute('data-titulo');
            document.getElementById('descripcion').value = button.getAttribute('data-descripcion');
            document.getElementById('curso_destino').value = button.getAttribute('data-curso');
            document.getElementById('fecha_vencimiento').value = button.getAttribute('data-fecha');
            document.getElementById('prioridad').value = button.getAttribute('data-prioridad');
            document.getElementById('estado').value = button.getAttribute('data-estado');
            document.getElementById('formEditar').action = '/editar_tarea';
        });
    });

    const btnProyecto = document.getElementById('proyecto-link');
    const btnCalendario = document.getElementById('calendario-link'); // ✅ nuevo
    const btnBackToTasksFromProjects = document.getElementById('btnBackToTasksFromProjects');
    const tasksContainer = document.getElementById('tasksContainer');
    const studentsContainer = document.getElementById('studentsContainer');
    const projectsContainer = document.getElementById('projectsContainer');
    const calendarioContainer = document.getElementById('contenido-calendario'); // ✅ nuevo

    // Event listener para el botón de refrescar archivos (usando event delegation)
    document.addEventListener('click', function (e) {
        if (e.target && e.target.id === 'btnRefrescarArchivos') {
            const modal = document.getElementById('modalVerDetallesTarea');
            if (modal && modal.classList.contains('show')) {
                const modalTitle = document.getElementById('detalleTareaTitle');
                if (modalTitle) {
                    const titleText = modalTitle.textContent;
                    const tareaActual = Array.from(document.querySelectorAll('.btnVerDetalles')).find(btn =>
                        btn.getAttribute('data-titulo') === titleText
                    );
                    if (tareaActual) {
                        cargarArchivosEnviados(tareaActual.getAttribute('data-id'));
                    }
                }
            }
        }
    });
    document.getElementById('archivo').addEventListener('change', function () {
        const archivo = this.files[0];
        if (archivo && archivo.size > 5 * 1024 * 1024) { // 5 MB en bytes
            alert('El archivo supera el límite de 5 MB.');
            this.value = '';  // Limpiar el input
        }
    });

    btnProyecto.addEventListener('click', function (e) {
        e.preventDefault();
        tasksContainer.style.display = 'none';
        studentsContainer.style.display = 'none';
        projectsContainer.style.display = 'block';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });

    btnCalendario.addEventListener('click', function (e) { // ✅ nuevo listener
        e.preventDefault();
        tasksContainer.style.display = 'none';
        studentsContainer.style.display = 'none';
        projectsContainer.style.display = 'none';
        calendarioContainer.style.display = 'block'; // ✅ mostrar calendario
        cargarCalendario(); // ✅ si quieres recargar calendario cada vez que entres
    });

    btnBackToTasksFromProjects.addEventListener('click', function () {
        projectsContainer.style.display = 'none';
        tasksContainer.style.display = 'block';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });
});

document.addEventListener('DOMContentLoaded', function () {
    const btnDashboard = document.getElementById('dashboard-link');
    const btnProyecto = document.getElementById('proyecto-link');
    const btnCalendario = document.getElementById('calendario-link'); // ✅ nuevo
    const btnBackToTasks = document.getElementById('btnBackToTasks');
    const btnBackToTasksFromProjects = document.getElementById('btnBackToTasksFromProjects');
    const tasksContainer = document.getElementById('tasksContainer');
    const studentsContainer = document.getElementById('studentsContainer');
    const projectsContainer = document.getElementById('projectsContainer');
    const calendarioContainer = document.getElementById('contenido-calendario'); // ✅ nuevo

    // Sidebar navigation for Tareas
    btnDashboard.addEventListener('click', function (e) {
        e.preventDefault();
        tasksContainer.style.display = 'block';
        studentsContainer.style.display = 'none';
        projectsContainer.style.display = 'none';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });

    // Sidebar navigation for Proyecto
    btnProyecto.addEventListener('click', function (e) {
        e.preventDefault();
        tasksContainer.style.display = 'none';
        studentsContainer.style.display = 'none';
        projectsContainer.style.display = 'block';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });

    // Sidebar navigation for Calendario ✅ nuevo
    btnCalendario.addEventListener('click', function (e) {
        e.preventDefault();
        tasksContainer.style.display = 'none';
        studentsContainer.style.display = 'none';
        projectsContainer.style.display = 'none';
        calendarioContainer.style.display = 'block'; // ✅ mostrar calendario
        cargarCalendario(); // ✅ si quieres recargar calendario cada vez que entres
    });

    // Back button from Students to Tareas
    btnBackToTasks.addEventListener('click', function () {
        studentsContainer.style.display = 'none';
        tasksContainer.style.display = 'block';
        projectsContainer.style.display = 'none';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });

    // Back button from Projects to Tareas
    btnBackToTasksFromProjects.addEventListener('click', function () {
        projectsContainer.style.display = 'none';
        tasksContainer.style.display = 'block';
        studentsContainer.style.display = 'none';
        calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
    });

    // Navigation for each group
    document.querySelectorAll('.curso-link-sidebar').forEach(function (grupoLink) {
        grupoLink.addEventListener('click', function (e) {
            e.preventDefault();
            const grupoNombre = this.textContent.trim();
            document.getElementById('studentsCourseTitle').querySelector('span').textContent = grupoNombre;
            tasksContainer.style.display = 'none';
            studentsContainer.style.display = 'block';
            projectsContainer.style.display = 'none';
            calendarioContainer.style.display = 'none'; // ✅ ocultar calendario
        });
    });
});

document.getElementById('proyecto-link').addEventListener('click', () => {
    document.getElementById('tasksContainer').style.display = 'none';
    document.getElementById('studentsContainer').style.display = 'none';
    document.getElementById('projectsContainer').style.display = 'block';
    document.getElementById('contenido-calendario').style.display = 'none'; // ✅ ocultar calendario
});

document.getElementById('btnBackToTasksFromProjects').addEventListener('click', () => {
    document.getElementById('tasksContainer').style.display = 'block';
    document.getElementById('studentsContainer').style.display = 'none';
    document.getElementById('projectsContainer').style.display = 'none';
    document.getElementById('contenido-calendario').style.display = 'none'; // ✅ ocultar calendario
});


document.addEventListener('DOMContentLoaded', function () {
    // Notificaciones para el líder
    function cargarNotificaciones() {
        fetch('/notificaciones')
            .then(res => res.json())
            .then(data => {
                const lista = document.getElementById('notificaciones-lista');
                const badge = document.getElementById('notificaciones-count');
                lista.innerHTML = '';
                let noLeidas = 0;
                if (data.notificaciones && data.notificaciones.length > 0) {
                    data.notificaciones.forEach(n => {
                        if (!n.leido) noLeidas++;
                        // Icono según tipo (puedes mejorar esto según tus tipos)
                        let icono = '<i class="bi bi-info-circle text-primary me-2"></i>';
                        if (n.mensaje && n.mensaje.toLowerCase().includes('complet')) {
                            icono = '<i class="bi bi-check-circle-fill text-success me-2"></i>';
                        }
                        // Fecha/hora
                        let fecha = '';
                        if (n.fecha) {
                            const d = new Date(n.fecha);
                            fecha = `<span class='noti-fecha ms-2 text-secondary small'>${d.toLocaleDateString()} ${d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>`;
                        }
                        // Truncar mensaje largo y mostrar tooltip
                        let mensaje = n.mensaje || '';
                        let mensajeCorto = mensaje.length > 48 ? mensaje.slice(0, 48) + '…' : mensaje;
                        let tooltip = mensaje.length > 48 ? `title='${mensaje.replace(/'/g, '&apos;')}'` : '';
                        const li = document.createElement('li');
                        li.className = 'noti-item px-2 py-2' + (n.leido ? ' noti-leida' : ' noti-noleida');
                        li.innerHTML = `
                            <div class="d-flex align-items-center justify-content-between gap-2">
                                <div class="d-flex align-items-center flex-grow-1">
                                    ${icono}
                                    <span class="noti-mensaje${n.leido ? ' text-muted' : ' fw-bold'}" style="max-width: 170px; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;" ${tooltip}>${mensajeCorto}</span>
                                    ${fecha}
                                </div>
                                ${!n.leido ? `<button class="btn btn-sm btn-link text-success p-0 ms-2 marcar-leida-btn" data-id="${n.id}" title="Marcar como leída"><i class="bi bi-check-circle"></i></button>` : ''}
                            </div>
                        `;
                        lista.appendChild(li);
                    });
                    badge.textContent = noLeidas;
                    lista.innerHTML += '<li><hr class="dropdown-divider"></li>';
                    lista.innerHTML += '<li><a class="dropdown-item text-primary text-center" href="#" id="marcarTodasLeidas">Marcar todas como leídas</a></li>';
                } else {
                    badge.textContent = '0';
                    lista.innerHTML = '<li><a class="dropdown-item text-center text-muted" href="#">No hay notificaciones</a></li>';
                    lista.innerHTML += '<li><hr class="dropdown-divider"></li>';
                    lista.innerHTML += '<li><a class="dropdown-item text-primary text-center" href="#" id="marcarTodasLeidas">Marcar todas como leídas</a></li>';
                }
                // Botón individual
                lista.querySelectorAll('.marcar-leida-btn').forEach(btn => {
                    btn.addEventListener('click', function(e) {
                        e.stopPropagation();
                        const id = this.getAttribute('data-id');
                        fetch('/notificaciones/marcar_leida', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({ id })
                        })
                        .then(res => res.json())
                        .then(resp => {
                            if (resp.success) cargarNotificaciones();
                        });
                    });
                });
                // Botón marcar todas
                const btnTodas = lista.querySelector('#marcarTodasLeidas');
                if (btnTodas) {
                    btnTodas.addEventListener('click', function(e) {
                        e.preventDefault();
                        if (data.notificaciones && data.notificaciones.length > 0) {
                            const ids = data.notificaciones.filter(n => !n.leido).map(n => n.id);
                            Promise.all(ids.map(id => fetch('/notificaciones/marcar_leida', {
                                method: 'POST',
                                headers: { 'Content-Type': 'application/json' },
                                body: JSON.stringify({ id })
                            }))).then(() => cargarNotificaciones());
                        }
                    });
                }
            });
    }
    // Cargar notificaciones al abrir el menú
    document.getElementById('navbarDropdownNotificaciones').addEventListener('click', cargarNotificaciones);
    // Polling automático cada 10 segundos
    setInterval(() => {
        // Solo refrescar si el menú está visible (abierto)
        const dropdown = document.getElementById('notificaciones-lista');
        if (dropdown && dropdown.offsetParent !== null) {
            cargarNotificaciones();
        }
    }, 10000); // 10 segundos
});

// Abrir modal para crear proyecto
document.getElementById('btnCrearProyecto').addEventListener('click', () => {
    document.getElementById('formProyecto').reset();
    document.getElementById('proyectoId').value = '';
    document.getElementById('formProyecto').action = '/crear_proyecto';
    document.getElementById('modalProyectoLabel').textContent = 'Crear Proyecto';
});

// Script para cargar datos al editar proyecto
document.querySelectorAll('.btnEditarProyecto').forEach(button => {
    button.addEventListener('click', () => {
        document.getElementById('formProyecto').reset();

        document.getElementById('proyectoId').value = button.getAttribute('data-id');
        document.getElementById('nombreProyecto').value = button.getAttribute('data-nombre');
        document.getElementById('descripcionProyecto').value = button.getAttribute('data-descripcion');
        document.getElementById('fechaInicio').value = button.getAttribute('data-fecha-inicio');
        document.getElementById('fechaFin').value = button.getAttribute('data-fecha-fin');

        document.getElementById('formProyecto').action = '/actualizar_proyecto/' + button.getAttribute('data-id');
        document.getElementById('modalProyectoLabel').textContent = 'Editar Proyecto';
    });
});
// ==== FUNCIONALIDAD PARA VER DETALLES DE TAREA ====

// Event listener para el botón "Ver Detalles"
document.addEventListener('DOMContentLoaded', function() {
    // Agregar event listeners a los botones "Ver Detalles"
    document.querySelectorAll('.btnVerDetalles').forEach(button => {
        button.addEventListener('click', function() {
            const tareaId = this.getAttribute('data-id');
            const titulo = this.getAttribute('data-titulo');
            const descripcion = this.getAttribute('data-descripcion');
            const curso = this.getAttribute('data-curso');
            const fecha = this.getAttribute('data-fecha');
            const prioridad = this.getAttribute('data-prioridad');
            const estado = this.getAttribute('data-estado');

            // Llenar la información básica del modal
            document.getElementById('detalleTareaTitle').textContent = titulo;
            document.getElementById('detalleTareaDescripcion').textContent = descripcion || 'Sin descripción';
            document.getElementById('detalleTareaCurso').textContent = curso;
            document.getElementById('detalleTareaFecha').textContent = fecha;

            // Configurar badges de estado y prioridad
            const estadoBadge = document.getElementById('detalleTareaEstado');
            const prioridadBadge = document.getElementById('detalleTareaPrioridad');

            // Badge de estado
            estadoBadge.className = `badge fs-6 mb-2 bg-${estado === 'completada' || estado === 'completado' ? 'success' : 'warning'}`;
            estadoBadge.textContent = estado === 'completada' || estado === 'completado' ? 'Completada' : 'Pendiente';

            // Badge de prioridad
            const prioridadClass = prioridad === 'alta' ? 'danger' : prioridad === 'media' ? 'warning' : 'secondary';
            prioridadBadge.className = `badge fs-6 bg-${prioridadClass}`;
            prioridadBadge.textContent = prioridad.charAt(0).toUpperCase() + prioridad.slice(1);

            // Cargar archivos enviados por trabajadores
            cargarArchivosEnviados(tareaId);
        });
    });
});

// Función para cargar archivos enviados por trabajadores
function cargarArchivosEnviados(tareaId) {
    const contenedorArchivos = document.getElementById('archivosEnviados');
    
    // Mostrar spinner de carga actualizado
    contenedorArchivos.innerHTML = `
        <div class="text-center py-3">
            <div class="spinner-border spinner-border-sm text-primary" role="status">
                <span class="visually-hidden">Cargando archivos...</span>
            </div>
            <p class="mt-2 mb-0 text-muted small">Cargando archivos enviados...</p>
        </div>
    `;

    // Hacer petición para obtener archivos de la tarea
    fetch(`/api/tarea/${tareaId}/archivos`)
        .then(response => response.json())
        .then(data => {
            if (data.archivos && data.archivos.length > 0) {
                let archivosHtml = '';
                
                data.archivos.forEach((archivo, index) => {
                    const fechaSubida = archivo.fecha_subida || 'Fecha no disponible';
                    const nombreUsuario = archivo.usuario || 'Usuario desconocido';
                    const tipoArchivo = obtenerTipoArchivo(archivo.nombre);
                    const iconoArchivo = obtenerIconoArchivo(tipoArchivo);
                    
                    archivosHtml += `
                        <div class="archivo-item">
                            <div class="d-flex align-items-center">
                                <i class="${iconoArchivo} text-primary fs-5 me-3"></i>
                                <div class="flex-grow-1">
                                    <h6 class="mb-1 text-truncate" title="${archivo.nombre}">
                                        ${archivo.nombre}
                                    </h6>
                                    <small class="text-muted d-block">
                                        <i class="bi bi-person me-1"></i>${nombreUsuario}
                                        <i class="bi bi-calendar3 ms-2 me-1"></i>${fechaSubida}
                                    </small>
                                </div>
                                <div class="d-flex gap-1">
                                    <a href="${archivo.url}" target="_blank" 
                                       class="btn btn-outline-primary btn-sm" 
                                       title="Descargar archivo">
                                        <i class="bi bi-download"></i>
                                    </a>
                                    <button class="btn btn-outline-secondary btn-sm" 
                                            onclick="previsualizarArchivo('${archivo.url}', '${archivo.nombre}')"
                                            title="Vista previa">
                                        <i class="bi bi-eye"></i>
                                    </button>
                                </div>
                            </div>
                        </div>
                    `;
                });
                
                contenedorArchivos.innerHTML = archivosHtml;
            } else {
                contenedorArchivos.innerHTML = `
                    <div class="text-center py-4">
                        <i class="bi bi-inbox fs-3 text-muted d-block mb-2"></i>
                        <h6 class="text-muted">No hay archivos enviados</h6>
                        <p class="mb-0 small text-muted">Los trabajadores aún no han enviado archivos para esta tarea.</p>
                    </div>
                `;
                
                // Resetear estadísticas
            }
        })
        .catch(error => {
            console.error('Error al cargar archivos:', error);
            contenedorArchivos.innerHTML = `
                <div class="text-center py-4">
                    <i class="bi bi-exclamation-circle fs-3 text-danger d-block mb-2"></i>
                    <h6 class="text-danger">Error al cargar archivos</h6>
                    <p class="mb-0 small text-muted">Ocurrió un error al cargar los archivos enviados.</p>
                </div>
            `;
        });
}

// Función para obtener el tipo de archivo
function obtenerTipoArchivo(nombreArchivo) {
    const extension = nombreArchivo.split('.').pop().toLowerCase();
    const tiposDocumentos = ['pdf', 'doc', 'docx', 'txt', 'rtf'];
    const tiposImagenes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg'];
    const tiposHojas = ['xls', 'xlsx', 'csv'];
    const tiposPresentaciones = ['ppt', 'pptx'];
    
    if (tiposDocumentos.includes(extension)) return 'documento';
    if (tiposImagenes.includes(extension)) return 'imagen';
    if (tiposHojas.includes(extension)) return 'hoja';
    if (tiposPresentaciones.includes(extension)) return 'presentacion';
    return 'generico';
}

// Función para obtener el ícono según el tipo de archivo
function obtenerIconoArchivo(tipo) {
    const iconos = {
        'documento': 'bi bi-file-text',
        'imagen': 'bi bi-file-image',
        'hoja': 'bi bi-file-spreadsheet',
        'presentacion': 'bi bi-file-slides',
        'generico': 'bi bi-file-earmark'
    };
    return iconos[tipo] || iconos['generico'];
}

// Función para previsualizar archivos (opcional)
function previsualizarArchivo(url, nombre) {
    const extension = nombre.split('.').pop().toLowerCase();
    
    if (['jpg', 'jpeg', 'png', 'gif', 'bmp'].includes(extension)) {
        // Previsualizar imagen
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${nombre}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body text-center">
                        <img src="${url}" class="img-fluid" alt="${nombre}">
                    </div>
                </div>
            </div>
        `;
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Eliminar modal del DOM cuando se cierre
        modal.addEventListener('hidden.bs.modal', () => {
            modal.remove();
        });
    } else {
        // Para otros tipos, abrir en nueva pestaña
        window.open(url, '_blank');
    }
}
function cargarArchivosDeTarea(tareaId) {
    const contenedor = document.getElementById('archivosEnviados');
    contenedor.innerHTML = `
        <div class="text-center">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Cargando archivos...</span>
            </div>
            <p class="mt-2 text-muted">Cargando archivos enviados...</p>
        </div>
    `;

    fetch(`/api/tarea/${tareaId}/archivos`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                contenedor.innerHTML = `<p class="text-danger">Error: ${data.error}</p>`;
                return;
            }

            document.getElementById('totalTrabajadores').textContent = data.estadisticas.total_trabajadores;
            document.getElementById('tareasCompletadas').textContent = data.estadisticas.tareas_completadas;
            document.getElementById('tareasPendientes').textContent = data.estadisticas.tareas_pendientes;

            const archivos = data.archivos;
            if (archivos.length === 0) {
                contenedor.innerHTML = `<p class="text-muted">No se han enviado archivos.</p>`;
                return;
            }

            const lista = document.createElement('ul');
            lista.className = 'list-group';

            archivos.forEach(archivo => {
                const item = document.createElement('li');
                item.className = 'list-group-item d-flex justify-content-between align-items-start';
                item.innerHTML = `
                    <div>
                        <strong>${archivo.usuario}</strong> envió:
                        <a href="${archivo.url}" target="_blank">${archivo.nombre}</a><br>
                        <small class="text-muted">${new Date(archivo.fecha_subida).toLocaleString()}</small>
                    </div>
                    <i class="bi bi-download text-primary fs-5"></i>
                `;
                lista.appendChild(item);
            });

            contenedor.innerHTML = '';
            contenedor.appendChild(lista);
        })
        .catch(err => {
            console.error(err);
            contenedor.innerHTML = `<p class="text-danger">Error al cargar archivos.</p>`;
        });
}

function abrirModalDetallesTarea(tareaId) {
    window.tareaActualId = tareaId;
    cargarArchivosDeTarea(tareaId);
    const modal = new bootstrap.Modal(document.getElementById('modalVerDetallesTarea'));
    modal.show();
}

document.getElementById('btnRefrescarArchivos').addEventListener('click', () => {
    if (window.tareaActualId) {
        cargarArchivosDeTarea(window.tareaActualId);
    }
});

document.getElementById('btnEditarPerfil').addEventListener('click', function (e) {
    e.preventDefault();  // 🔴 SIN ESTO, SE RECARGA LA PÁGINA

    fetch('/obtener_perfil_lider')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                document.getElementById('perfilNombre').value = data.nombre;
                document.getElementById('perfilCorreo').value = data.correo;
                document.getElementById('perfilTelefono').value = data.telefono || '';
                document.getElementById('perfilDireccion').value = data.direccion || '';
                document.getElementById('perfilDescripcion').value = data.descripcion || '';

                document.getElementById('contraseñaActual').value = '';
                document.getElementById('nuevaContraseña').value = '';
                document.getElementById('confirmarContraseña').value = '';

                const modalPerfil = new bootstrap.Modal(document.getElementById('modalPerfilLider'));
                modalPerfil.show();
            } else {
                alert('Error al cargar perfil');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al cargar perfil');
        });
});


// Manejar el envío del formulario de perfil
document.getElementById('formPerfilLider').addEventListener('submit', function (e) {
    e.preventDefault();
    
    const formData = new FormData(this);
    
    fetch('/actualizar_perfil_lider', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Perfil actualizado correctamente');
            bootstrap.Modal.getInstance(document.getElementById('modalPerfilLider')).hide();
            // Recargar la página para actualizar la información mostrada
            location.reload();
        } else {
            alert(data.message || 'Error al actualizar perfil');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('Error al actualizar perfil');
    });
});

let usuarioChatActual = null;

// Cargar lista de chats: mostrar admin + trabajadores del mismo grupo
function cargarListaChats() {
  Promise.all([
    fetch('/api/chat/trabajadores'),  // Trabajadores del mismo grupo
    fetch('/api/administrador/chat')  // Admin
  ])
    .then(([resTrabajadores, resAdmin]) => 
      Promise.all([resTrabajadores.json(), resAdmin.json()])
    )
    .then(([trabajadores, admin]) => {
      const lista = document.getElementById('chat-list');
      lista.innerHTML = '';
      
      // Agregar admin primero si existe
      if (admin && admin.id) {
        const div = document.createElement('div');
        div.classList.add('chat-list-item');
        div.innerHTML = `
          <img src="${admin.foto || '/static/avatars/default.png'}" class="chat-avatar-mini">
          <div>
            <div><strong>${admin.nombre_completo}</strong> <span class="badge bg-danger ms-1">Admin</span></div>
            <small>Haz clic para abrir el chat</small>
          </div>`;
        div.onclick = () => abrirChatPopup(admin.id, admin.nombre_completo, admin.foto);
        lista.appendChild(div);
      }
      
      // Agregar trabajadores del mismo grupo
      trabajadores.forEach(trab => {
        const div = document.createElement('div');
        div.classList.add('chat-list-item');
        div.innerHTML = `
          <img src="${trab.foto || '/static/avatars/default.png'}" class="chat-avatar-mini">
          <div>
            <div><strong>${trab.nombre_completo}</strong> <span class="badge bg-success ms-1">Trabajador</span></div>
            <small>Haz clic para abrir el chat</small>
          </div>`;
        div.onclick = () => abrirChatPopup(trab.id, trab.nombre_completo, trab.foto);
        lista.appendChild(div);
      });
    })
    .catch(err => console.error('Error cargando lista de chats:', err));
}

function abrirChatPopup(id, nombre, foto) {
  usuarioChatActual = id;
  document.getElementById('chat-messenger').style.display = 'none';
  document.getElementById('chat-popup').style.display = 'flex';
  document.getElementById('chat-nombre').textContent = nombre;
  document.getElementById('chat-avatar').src = foto || '/static/avatars/default.png';
  cargarMensajesPopup(id);
}

function cerrarChatPopup() {
  document.getElementById('chat-popup').style.display = 'none';
  document.getElementById('chat-popup-mensajes').innerHTML = '';
  usuarioChatActual = null;
}

function cargarMensajesPopup(receptorId) {
  fetch(`/api/chat/${receptorId}`)
    .then(res => res.json())
    .then(mensajes => {
      const contenedor = document.getElementById('chat-popup-mensajes');
      contenedor.innerHTML = '';
      mensajes.forEach(m => agregarMensajeAlPopup(m));
      contenedor.scrollTop = contenedor.scrollHeight;
    });
}

document.getElementById('chat-popup-form').addEventListener('submit', e => {
  e.preventDefault();
  const input = document.getElementById('chat-popup-input');
  const mensaje = input.value.trim();
  if (!mensaje || !usuarioChatActual) return;

  // Usar Socket.IO para enviar mensaje en tiempo real
  if (typeof socket !== 'undefined') {
    socket.emit('enviar_mensaje', {
      receptor_id: usuarioChatActual,
      mensaje: mensaje,
      tipo: 'texto'
    });
  } else {
    // Fallback a HTTP si Socket.IO no está disponible
    fetch('/api/chat/enviar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receptor_id: usuarioChatActual, mensaje })
    }).then(() => {
      cargarMensajesPopup(usuarioChatActual);
    });
  }

  input.value = '';
});

document.getElementById('chat-popup-img').addEventListener('change', function () {
  const file = this.files[0];
  if (!file || !usuarioChatActual) return;
  
  // Para imágenes, seguimos usando HTTP ya que Socket.IO no maneja archivos directamente
  const formData = new FormData();
  formData.append('imagen', file);
  formData.append('receptor_id', usuarioChatActual);

  fetch('/api/chat/enviar-imagen', {
    method: 'POST',
    body: formData
  }).then(() => {
    cargarMensajesPopup(usuarioChatActual);
  });
});

function mostrarImagenGrande(src) {
  const modal = document.createElement("div");
  modal.style.position = "fixed";
  modal.style.top = 0;
  modal.style.left = 0;
  modal.style.width = "100vw";
  modal.style.height = "100vh";
  modal.style.background = "rgba(0,0,0,0.8)";
  modal.style.display = "flex";
  modal.style.alignItems = "center";
  modal.style.justifyContent = "center";
  modal.style.zIndex = 9999;
  modal.innerHTML = `<img src="${src}" style="max-width:90%; max-height:90%; border-radius: 10px;">`;
  modal.onclick = () => modal.remove();
  document.body.appendChild(modal);
}

document.getElementById('minimizar-chat-popup').addEventListener('click', () => {
  document.getElementById('chat-popup').style.display = 'none';
  document.getElementById('chat-messenger').style.display = 'flex';
});

document.getElementById('chat-fab').addEventListener('click', () => {
  cargarListaChats();
  document.getElementById('chat-messenger').style.display = 'flex';
});

document.getElementById('close-chat-messenger').addEventListener('click', () => {
  document.getElementById('chat-messenger').style.display = 'none';
});

// Función para sincronizar mensajes periódicamente (respaldo)
function sincronizarMensajes() {
  if (usuarioChatActual) {
    cargarMensajesPopup(usuarioChatActual);
  }
}

// Actualizar mensajes cada 5 segundos como respaldo
setInterval(sincronizarMensajes, 5000);
