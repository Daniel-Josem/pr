// JS para vista previa y AJAX de perfil

document.addEventListener('DOMContentLoaded', function() {
  const inputAvatar = document.getElementById('perfil-avatar');
  const previewImg = document.getElementById('avatar-preview');
  const actualImg = document.getElementById('avatar-actual');
  const form = document.getElementById('formPerfil');
  const mensaje = document.getElementById('mensajePerfil');
  const btnGuardar = document.getElementById('btn-guardar-perfil');
  const btnText = document.getElementById('perfil-btn-text');
  const btnSpinner = document.getElementById('perfil-btn-spinner');
  // Elementos para actualizar nombre y acerca de mí en la página
  const nombreDisplay = document.querySelector('.user-nombre, #user-nombre');
  const acercaDisplay = document.querySelector('.user-acerca, #user-acerca');
  const avatarCabecera = document.getElementById('avatar-cabecera');

  // Vista previa de avatar
  if (inputAvatar) {
    inputAvatar.addEventListener('change', function(e) {
      const file = e.target.files[0];
      if (file) {
        const reader = new FileReader();
        reader.onload = function(ev) {
          previewImg.src = ev.target.result;
          previewImg.style.display = 'inline-block';
        };
        reader.readAsDataURL(file);
      } else {
        previewImg.src = '';
        previewImg.style.display = 'none';
      }
    });
  }

  // Envío AJAX del formulario de perfil
  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      mensaje.textContent = '';
      mensaje.className = 'mt-2 fw-bold';
      btnGuardar.disabled = true;
      btnText.textContent = 'Guardando...';
      btnSpinner.style.display = 'inline-block';
      try {
        const formData = new FormData(form);
        // Asegurarse de enviar el campo descripcion aunque no se haya cambiado
        const descripcion = form['descripcion'] ? form['descripcion'].value : '';
        formData.set('descripcion', descripcion);
        const resp = await fetch('/api/actualizar_foto', {
          method: 'POST',
          body: formData
        });
        const data = await resp.json();
        if (resp.ok && data.success) {
          // Actualiza avatar en el DOM usando la URL devuelta (con anti-caché)
          if (data.foto_url) {
            if (actualImg) actualImg.src = data.foto_url;
            if (avatarCabecera) avatarCabecera.src = data.foto_url;
            if (previewImg) previewImg.style.display = 'none';
          }
          // Actualiza nombre y descripción si el backend los devuelve
          if (data.nombre && nombreDisplay) nombreDisplay.textContent = data.nombre;
          if (form['nombre'] && data.nombre) form['nombre'].value = data.nombre;
          if (form['descripcion'] && data.acerca_de_mi !== undefined) form['descripcion'].value = data.acerca_de_mi;
          if (acercaDisplay && data.acerca_de_mi !== undefined) acercaDisplay.textContent = data.acerca_de_mi;
          mensaje.textContent = '¡Perfil actualizado!';
          mensaje.className = 'mt-2 text-success fw-bold';
          // Cierra el modal después de actualizar el DOM
          setTimeout(() => {
            const modal = bootstrap.Modal.getInstance(document.getElementById('perfilModal'));
            if (modal) modal.hide();
          }, 600);
        } else {
          mensaje.textContent = data.error || 'Error al actualizar el perfil.';
          mensaje.className = 'mt-2 text-danger fw-bold';
        }
      } catch (err) {
        mensaje.textContent = 'Error de red o servidor.';
        mensaje.className = 'mt-2 text-danger fw-bold';
      } finally {
        btnGuardar.disabled = false;
        btnText.textContent = 'Guardar cambios';
        btnSpinner.style.display = 'none';
      }
    });
  }
});


//notificaciones

        // Mostrar la sección correspondiente al hacer clic en el menú lateral
        document.addEventListener('DOMContentLoaded', function() {
          const secciones = [
            'seccion-inicio',
            'seccion-mis-tareas',
            'contenido-planificacion',
            'contenido-calendario',
            'seccion-estadisticas',
            'seccion-ayuda'
          ];
          
          function mostrarSeccion(id) {
            // Ocultar todas las secciones
            secciones.forEach(sec => {
              const el = document.getElementById(sec);
              if (el) {
                el.classList.remove('active');
              }
            });
            // Mostrar la sección seleccionada
            const seccionActiva = document.getElementById(id);
            if (seccionActiva) {
              seccionActiva.classList.add('active');
            }
            // Actualizar estado activo del menú
            document.querySelectorAll('#sidebar .nav-link').forEach(link => {
              link.classList.remove('active');
            });
            // Marcar como activo el enlace correspondiente
            const linkActivo = document.querySelector(`#sidebar .nav-link[onclick*="${id}"], #sidebar .nav-link[data-section="${id}"]`);
            if (linkActivo) {
              linkActivo.classList.add('active');
            }
          }
          
          document.getElementById('btn-inicio')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('seccion-inicio');
          });
          document.getElementById('btn-mis-tareas')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('seccion-mis-tareas');
          });
          document.getElementById('btn-planificacion')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('contenido-planificacion');
          });
          document.getElementById('btn-calendario')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('contenido-calendario');
          });
          document.getElementById('btn-estadisticas')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('seccion-estadisticas');
          });
          document.getElementById('btn-ayuda')?.addEventListener('click', function(e) {
            e.preventDefault();
            mostrarSeccion('seccion-ayuda');
          });
          
          // Mostrar la sección de inicio por defecto
          mostrarSeccion('seccion-inicio');
        });
      
// Notificaciones trabajador
async function cargarNotificaciones() {
  try {
    const resp = await fetch('/api/notificaciones');
    const data = await resp.json();
    const lista = document.getElementById('notificaciones-lista');
    if (data.ok && data.notificaciones.length > 0) {
      lista.innerHTML = data.notificaciones.map(n =>
        `<li class="dropdown-item small">${n.mensaje} <br><span class="text-muted">${n.fecha || ''}</span></li>`
      ).join('');
    } else {
      lista.innerHTML = '<li class="text-muted small">🔔 No hay notificaciones nuevas</li>';
    }
  } catch (e) {
    document.getElementById('notificaciones-lista').innerHTML = '<li class="text-danger small">Error al cargar notificaciones</li>';
  }
}
document.getElementById('dropdownNotificaciones')?.addEventListener('click', cargarNotificaciones);




document.addEventListener('DOMContentLoaded', function() {
      // Si no hay tareas, no hacer nada
      if (!window.tareasUsuario || !Array.isArray(window.tareasUsuario)) return;

      const tareas = window.tareasUsuario;
      let total = tareas.length;
      let completadas = 0;
      let enProgreso = 0;
      let atrasadas = 0;

      // Fecha actual (sin hora)
      const hoy = new Date();
      hoy.setHours(0,0,0,0);

      tareas.forEach(tarea => {
        // Normalizar el estado para lógica de trabajador:
        // "pendiente" (asignado por líder) cuenta como "en progreso" para el trabajador
        let estado = (tarea.estado || '').toLowerCase();
        if (estado === 'pendiente') {
          estado = 'en progreso';
        }
        // Completadas
        if (estado === 'completado' || estado === 'completada') {
          completadas++;
        } else if (estado === 'en progreso') {
          // Si la fecha de vencimiento ya pasó, cuenta como atrasada
          if (tarea.fecha_vencimiento) {
            const fechaVenc = new Date(tarea.fecha_vencimiento);
            fechaVenc.setHours(0,0,0,0);
            if (fechaVenc < hoy) {
              atrasadas++;
              return;
            }
          }
          enProgreso++;
        }
      });

      // Actualizar los contadores en el DOM
      const setText = (id, val) => {
        const el = document.getElementById(id);
        if (el) el.textContent = val;
      };
      setText('total-tareas-js', total);
      setText('tareas-completadas-js', completadas);
      setText('tareas-progreso-js', enProgreso);
      setText('tareas-atrasadas-js', atrasadas);
    });
