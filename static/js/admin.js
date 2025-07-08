document.addEventListener('DOMContentLoaded', function () {
  const mainContent = document.getElementById('mainContent');
  const statsEl = document.getElementById('stats');
  const dashboardLink = document.getElementById('dashboard-link');
  const profesoresLink = document.getElementById('profesores-link');
  const registroLink = document.getElementById('registro-profesor-link');
  const trabajadoresLink = document.getElementById('trabajadores-link');
  const crearProyectoLink = document.getElementById('crear-proyecto-link');
  const seguimientoLink = document.getElementById('seguimiento-link');
  const Asignacionlink = document.getElementById('Asignacion-link');

  function ocultarSecciones() {
    if (statsEl) statsEl.style.display = 'none';
    mainContent.innerHTML = '';
  }

  function cargarEstadisticas() {
    if (statsEl) statsEl.style.display = 'flex';
  }
//Parte del Dashboard
if (dashboardLink) {
    dashboardLink.addEventListener('click', e => {
      e.preventDefault();
      cargarEstadisticas();
      mainContent.innerHTML = '';
    });
  }
  fetch('/api/trabajadores/count')
    .then(response => response.json())
    .then(data => {
      document.getElementById('trabajadores-count').textContent = data.count;
    })
    .catch(error => console.error('Error al obtener trabajadores:', error));

  fetch('/api/lider/count')
    .then(response => response.json())
    .then(data => {
      document.getElementById('lideres-count').textContent = data.count;
    })
    .catch(error => console.error('Error al obtener líderes:', error));
  
    fetch('/api/proyectos/count')
    .then(response => response.json())
    .then(data => {
      document.getElementById('proyectos-count').textContent = data.count;
    })
    .catch(error => console.error('Error al obtener proyectos:', error));


//Parte de Registro de lideres
    if (registroLink) {
  registroLink.addEventListener("click", function (e) {
    e.preventDefault();
    ocultarSecciones();

    const formularioHTML = `
      <div class="container mt-4">
        <h3 class="mb-4">Registrar Nuevo Líder</h3>
        <form id="formRegistroLider">
          <div class="row g-3">
            <div class="col-md-6"><label class="form-label">Nombre</label><input type="text" class="form-control" name="nombre" required></div>
            <div class="col-md-6"><label class="form-label">Apellido</label><input type="text" class="form-control" name="apellido" required></div>
            <div class="col-md-6"><label class="form-label">Usuario</label><input type="text" class="form-control" name="usuario" required></div>
            <div class="col-md-6"><label class="form-label">Contraseña</label><input type="password" class="form-control" name="contrasena" required></div>
            <div class="col-md-6"><label class="form-label">Documento</label><input type="text" class="form-control" name="documento" required></div>
            <div class="col-md-6"><label class="form-label">Proyecto</label>
              <select class="form-select" name="proyecto" id="selectProyecto" required>
                <option disabled selected value="">Cargando proyectos...</option>
              </select>
            </div>
            <div class="col-md-6"><label class="form-label">Grupo</label><input type="text" name="grupo" id="grupoInput" class="form-control" placeholder="Grupo del proyecto" readonly required></div>
            <div class="col-md-6"><label class="form-label">Correo Electrónico</label><input type="email" class="form-control" name="correo" required></div>
            <div class="col-md-6"><label class="form-label">Teléfono</label><input type="text" class="form-control" name="telefono" required></div>
            <div class="col-md-6"><label class="form-label">Dirección</label><input type="text" class="form-control" name="direccion" required></div>
          </div>
          <div class="mt-4">
            <button type="submit" class="btn btn-success">Registrar</button>
          </div>
        </form>
      </div>
    `;

    mainContent.innerHTML = formularioHTML;

    // Cargar proyectos activos en el <select>
    obtenerProyectosActivos().then(proyectos => {
      const selectProyecto = document.getElementById("selectProyecto");
      selectProyecto.innerHTML = `<option disabled selected value="">Selecciona un proyecto</option>`;
      proyectos.forEach(p => {
        const option = document.createElement("option");
        option.value = p.nombre;
        option.dataset.grupo = p.grupo;
        option.textContent = p.nombre;
        selectProyecto.appendChild(option);
      });
    });

    async function obtenerProyectosActivos() {
      try {
        const res = await fetch('/api/proyectos');
        if (!res.ok) throw new Error('Error al obtener proyectos');
        return await res.json();
      } catch (err) {
        console.error('Error cargando proyectos:', err);
        return [];
      }
    }

    // Cambiar automáticamente el grupo según proyecto
    document.getElementById("selectProyecto").addEventListener("change", function (e) {
      const grupo = e.target.selectedOptions[0].dataset.grupo;
      document.getElementById("grupoInput").value = grupo || "";
    });

    // Manejar el envío del formulario
    const formRegistro = document.getElementById("formRegistroLider");
    formRegistro.addEventListener("submit", function (e) {
      e.preventDefault();

      const datos = {
        nombre: formRegistro.nombre.value,
        apellido: formRegistro.apellido.value,
        usuario: formRegistro.usuario.value,
        contrasena: formRegistro.contrasena.value,
        documento: formRegistro.documento.value,
        proyecto: formRegistro.proyecto.value,
        grupo: formRegistro.grupo.value,
        correo: formRegistro.correo.value,
        telefono: formRegistro.telefono.value,
        direccion: formRegistro.direccion.value
      };

      fetch('/api/lideres/crear', {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(datos)
      })
        .then((res) => res.json())
        .then((data) => {
          if (data.message) {
            alert("✅ " + data.message);
            formRegistro.reset();
            document.getElementById("grupoInput").value = "";
            document.getElementById("selectProyecto").selectedIndex = 0;
            document.getElementById("profesores-link").click();
          } else if (data.error) {
            alert("❌ " + data.error);
          }
        })
        .catch((error) => {
          console.error("Error en el registro:", error);
          alert("❌ Error en el servidor.");
        });
    });
  });
}

//Parte de lideres
const formRegistro = document.getElementById('formRegistroLider');
      if (formRegistro) {
        formRegistro.addEventListener('submit', function (e) {
          e.preventDefault();
          const formData = new FormData(this);
          const data = Object.fromEntries(formData.entries());

          fetch('/api/lideres/crear', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
          })
          .then(res => res.json())
          .then(response => {
            if (response.message) {
              alert("✅ " + response.message);
              formRegistro.reset();

              fetch('/api/lideres')
                .then(res => res.json())
                .then(lideres => {
                  let tablaHTML = `
                    <h3 class="mb-4">Lista de Líderes</h3>
                    <table class="table table-bordered table-hover">
                      <thead class="table-light">
                        <tr>
                          <th>ID</th>
                          <th>Nombre</th>
                          <th>Usuario</th>
                          <th>Documento</th>
                          <th>Grupo</th>
                          <th>Proyecto</th>
                          <th>Correo</th>
                          <th>Teléfono</th>
                          <th>Dirección</th>
                          <th>Estado</th>
                          <th>Acciones</th>
                        </tr>
                      </thead>
                      <tbody>`;
                  lideres.forEach(l => {
                    tablaHTML += `
                      <tr id="fila-lider-${l.id}">
                        <td>${l.id}</td>
                        <td><span class="nombre-lider-clickable" data-id="${l.id}">${l.nombre_completo}</span></td>
                        <td>${l.nombre_usuario}</td>
                        <td>${l.documento}</td>
                        <td>${l.grupo}</td>
                        <td>${l.proyecto}</td>
                        <td>${l.correo}</td>
                        <td>${l.telefono}</td>
                        <td>${l.direccion}</td>
                        <td><span class="badge ${l.estado === 'activo' ? 'bg-success' : 'bg-secondary'}">${l.estado}</span></td>
                        <td>
                          ${l.estado === 'activo'
                            ? `<button class="btn btn-danger btn-sm inactivar-lider" data-id="${l.id}">Inactivar</button>`
                            : `<button class="btn btn-secondary btn-sm" disabled>Inactivado</button>`}
                        </td>
                      </tr>`;
                  });
                  tablaHTML += `</tbody></table>`;
                  mainContent.innerHTML = tablaHTML;
                  cargarEventosLideres();
                });
            } else if (response.error) {
              alert("❌ Error: " + response.error);
            }
          })
          .catch(err => {
            console.error("Error al registrar líder:", err);
            alert("❌ Error al registrar líder.");
          });
        });
      }

       if (profesoresLink) {
    profesoresLink.addEventListener('click', function (e) {
      e.preventDefault();
      ocultarSecciones();

      fetch('/api/lideres')
        .then(res => res.json())
        .then(lideres => {
          let tablaHTML = `
            <h3 class="mb-4">Lista de Líderes</h3>
            <table class="table table-bordered table-hover">
              <thead class="table-light">
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Usuario</th>
                  <th>Documento</th>
                  <th>Grupo</th>
                  <th>Proyecto</th>
                  <th>Correo</th>
                  <th>Teléfono</th>
                  <th>Dirección</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>`;
          lideres.forEach(l => {
            tablaHTML += `
              <tr id="fila-lider-${l.id}">
                <td>${l.id}</td>
                <td><span class="nombre-lider-clickable" data-id="${l.id}">${l.nombre_completo}</span></td>
                <td>${l.nombre_usuario}</td>
                <td>${l.documento}</td>
                <td>${l.grupo}</td>
                <td>${l.proyecto}</td>
                <td>${l.correo}</td>
                <td>${l.telefono}</td>
                <td>${l.direccion}</td>
                <td><span class="badge ${l.estado === 'activo' ? 'bg-success' : 'bg-secondary'}">${l.estado}</span></td>
                <td>
                  ${l.estado === 'activo'
                    ? `<button class="btn btn-danger btn-sm inactivar-lider" data-id="${l.id}">Inactivar</button>`
                    : `<button class="btn btn-secondary btn-sm" disabled>Inactivado</button>`}
                </td>
              </tr>`;
          });
          tablaHTML += `</tbody></table>`;
          mainContent.innerHTML = tablaHTML;
          cargarEventosLideres();
        })
        .catch(error => console.error('Error al cargar líderes:', error));
    });
  }
function cargarEventosLideres() {
  // Activar botón "Inactivar"
  document.querySelectorAll('.inactivar-lider').forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.dataset.id;

      fetch(`/api/lider/inactivar/${id}`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(data => {
          alert("🚫 " + data.message);

          // ✅ Borrar visualmente la fila
          const fila = document.getElementById(`fila-lider-${id}`);
          if (fila) fila.remove();  // ✅ Esto mantiene el registro en la BD pero lo quita visualmente
         
          // ✅ Actualizar contador de líderes tras inactivación
          fetch('/api/lider/count')
            .then(response => response.json())
            .then(data => {
              document.getElementById('lideres-count').textContent = data.count;
  });

        })
        .catch(err => console.error("Error al inactivar líder:", err));
    });
  });

    document.querySelectorAll('.nombre-lider-clickable').forEach(span => {
    span.addEventListener('click', function () {
      const id = this.dataset.id;
      fetch(`/api/lider/${id}`)
        .then(res => res.json())
        .then(l => {
          mainContent.innerHTML = `
            <div class="container mt-4">
              <h3>Editar Líder</h3>
              <form id="formEditarLider">
                <input type="hidden" name="id" value="${l.id}">
                <div class="row g-3">
                  <div class="col-md-6"><label class="form-label">Nombre Completo</label><input type="text" name="nombre_completo" class="form-control" value="${l.nombre_completo}" required></div>
                  <div class="col-md-6"><label class="form-label">Usuario</label><input type="text" name="nombre_usuario" class="form-control" value="${l.nombre_usuario}" required></div>
                  <div class="col-md-6"><label class="form-label">Documento</label><input type="text" name="documento" class="form-control" value="${l.documento}" required></div>
                  <div class="col-md-6"><label class="form-label">Grupo</label><input type="text" name="grupo" class="form-control" value="${l.grupo || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Proyecto</label><input type="text" name="proyecto" class="form-control" value="${l.proyecto || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Correo</label><input type="email" name="correo" class="form-control" value="${l.correo}" required></div>
                  <div class="col-md-6"><label class="form-label">Teléfono</label><input type="text" name="telefono" class="form-control" value="${l.telefono || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Dirección</label><input type="text" name="direccion" class="form-control" value="${l.direccion || ''}"></div>
                </div>
                <div class="mt-3"><button type="submit" class="btn btn-primary">Guardar Cambios</button></div>
              </form>
            </div>
          `;

          const formEditar = document.getElementById('formEditarLider');
          formEditar.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const datos = Object.fromEntries(formData.entries());

            fetch('/api/lider/actualizar', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(datos)
            })
              .then(res => res.json())
              .then(response => {
                alert("✅ " + response.message);
                document.getElementById('profesores-link').click();
              })
              .catch(error => {
                alert("❌ Error al actualizar líder");
                console.error(error);
              });
          });
        });
    });
  });

}
//Parte de Trabajadores
if (trabajadoresLink) {
  trabajadoresLink.addEventListener('click', function (e) {
    e.preventDefault();
    ocultarSecciones();

    fetch('/api/trabajadores')
      .then(res => res.json())
      .then(trabajadores => {
        let tablaHTML = `
          <h3 class="mb-4">Lista de Trabajadores</h3>
          <table class="table table-bordered table-hover">
            <thead class="table-light">
              <tr>
                <th>ID</th>
                <th>Nombre</th>
                <th>Usuario</th>
                <th>Documento</th>
                <th>Correo</th>
                <th>Grupo</th>
                <th>Proyecto</th>
                <th>Estado</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>`;

        trabajadores.forEach(t => {
          tablaHTML += `
            <tr id="fila-trabajador-${t.id}">
              <td>${t.id}</td>
              <td><span class="nombre-trabajador-clickable" data-id="${t.id}">${t.nombre_completo}</span></td>
              <td>${t.nombre_usuario}</td>
              <td>${t.documento}</td>
              <td>${t.correo}</td>
              <td>${t.grupo}</td>
              <td>${t.proyecto || ''}</td>
              <td><span class="badge ${t.estado === 'activo' ? 'bg-success' : 'bg-secondary'}">${t.estado}</span></td>
              <td>
                ${t.estado === 'activo'
                  ? `<button class="btn btn-danger btn-sm inactivar-trabajador" data-id="${t.id}">Inactivar</button>`
                  : `<button class="btn btn-secondary btn-sm" disabled>Inactivado</button>`}
              </td>
            </tr>`;
        });

        tablaHTML += `</tbody></table>`;
        mainContent.innerHTML = tablaHTML;
        cargarEventosTrabajadores();
      });
  });
}
function cargarEventosTrabajadores() {
  document.querySelectorAll('.inactivar-trabajador').forEach(btn => {
    btn.addEventListener('click', function () {
      const id = this.dataset.id;

      fetch(`/api/trabajador/inactivar/${id}`, {
        method: 'POST'
      })
        .then(res => res.json())
        .then(data => {
          alert("🚫 " + data.message);
          const fila = document.getElementById(`fila-trabajador-${id}`);
          if (fila) fila.remove();
        })
        .catch(err => console.error("Error al inactivar trabajador:", err));
    });
  });

  document.querySelectorAll('.nombre-trabajador-clickable').forEach(span => {
    span.addEventListener('click', function () {
      const id = this.dataset.id;
      fetch(`/api/trabajador/${id}`)
        .then(res => res.json())
        .then(t => {
          mainContent.innerHTML = `
            <div class="container mt-4">
              <h3>Editar Trabajador</h3>
              <form id="formEditarTrabajador">
                <input type="hidden" name="id" value="${t.id}">
                <div class="row g-3">
                  <div class="col-md-6"><label class="form-label">Nombre Completo</label><input type="text" name="nombre_completo" class="form-control" value="${t.nombre_completo}" required></div>
                  <div class="col-md-6"><label class="form-label">Usuario</label><input type="text" name="nombre_usuario" class="form-control" value="${t.nombre_usuario}" required></div>
                  <div class="col-md-6"><label class="form-label">Documento</label><input type="text" name="documento" class="form-control" value="${t.documento}" required></div>
                  <div class="col-md-6"><label class="form-label">Grupo</label><input type="text" name="grupo" class="form-control" value="${t.grupo || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Proyecto</label><input type="text" name="proyecto" class="form-control" value="${t.proyecto || ''}"></div>
                  <div class="col-md-6"><label class="form-label">Correo</label><input type="email" name="correo" class="form-control" value="${t.correo}" required></div>
                </div>
                <div class="mt-3"><button type="submit" class="btn btn-primary">Guardar Cambios</button></div>
              </form>
            </div>
          `;

          const formEditar = document.getElementById('formEditarTrabajador');
          formEditar.addEventListener('submit', function (e) {
            e.preventDefault();
            const formData = new FormData(this);
            const datos = Object.fromEntries(formData.entries());

            fetch('/api/trabajador/actualizar', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify(datos)
            })
              .then(res => res.json())
              .then(response => {
                alert("✅ " + response.message);
                trabajadoresLink.click(); // recargar lista
              })
              .catch(error => {
                alert("❌ Error al actualizar trabajador");
                console.error(error);
              });
          });
        });
    });
  });

}
//Parte del perfil del administrador
document.getElementById('imagenPerfilInput').addEventListener('change', function (e) {
  const file = e.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = function (event) {
      document.getElementById('previewImagenPerfil').src = event.target.result;
      document.querySelector('.user-pill img').src = '/static/avatars/perfil.jpeg?t=' + new Date().getTime();

    };
    reader.readAsDataURL(file);
  }
});

document.getElementById('formPerfil').addEventListener('submit', function (e) {
  e.preventDefault();

  const form = e.target;
  const formData = new FormData(form);

  fetch('/perfil/actualizar', {
    method: 'POST',
    body: formData
  })
    .then(res => res.json())
    .then(data => {
      if (data.imagen) {
        // Cambiar imagen del menú superior inmediatamente
        const avatar = document.querySelector('.user-pill img');
        avatar.src = data.imagen + '?t=' + new Date().getTime(); // Cache busting

        // También cambiar en el modal
        document.getElementById('previewImagenPerfil').src = data.imagen + '?t=' + new Date().getTime();
      }

      // Cambiar nombre
      if (data.nombre) {
        document.querySelector('.user-name').textContent = data.nombre;
      }

      // Cerrar modal
      const modal = bootstrap.Modal.getInstance(document.getElementById('perfilModal'));
      modal.hide();
    })
    .catch(err => {
      alert('Error al actualizar perfil');
      console.error(err);
    });
});

//Parte de Crear proyectos
if (crearProyectoLink) {
  crearProyectoLink.addEventListener('click', function (e) {
    e.preventDefault();
    mostrarVistaCrearProyectos();
  });
}

function mostrarVistaCrearProyectos() {
  ocultarSecciones();
  const html = `
    <h3>Gestión de Proyectos</h3>
    <form id="formCrearProyecto" class="mb-4">
      <div class="row">
        <div class="col-md-6 mb-3">
          <input type="text" class="form-control" id="nombreProyecto" placeholder="Nombre del proyecto" required>
        </div>
        <div class="col-md-6 mb-3">
          <input type="text" class="form-control" id="grupoProyecto" placeholder="Grupo" required>
        </div>
        <div class="col-12 mb-3">
          <textarea class="form-control" id="descripcionProyecto" placeholder="Descripción" required></textarea>
        </div>
        <div class="col-md-6 mb-3">
          <label>Fecha de inicio</label>
          <input type="date" class="form-control" id="fechaInicio" required>
        </div>
        <div class="col-md-6 mb-3">
          <label>Fecha de finalización</label>
          <input type="date" class="form-control" id="fechaFin" required>
        </div>
        <div class="col-12">
          <button type="submit" class="btn btn-success">Crear Proyecto</button>
        </div>
      </div>
    </form>

    <table class="table table-bordered table-striped">
      <thead>
        <tr>
          <th>Nombre</th>
          <th>Descripción</th>
          <th>Inicio</th>
          <th>Finalización</th>
          <th>Grupo</th>
          <th>Estado</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody id="tablaProyectosBody"></tbody>
    </table>
  `;

  document.getElementById('mainContent').innerHTML = html;

  document.getElementById('formCrearProyecto').addEventListener('submit', function (e) {
    e.preventDefault();
    const data = {
      nombre: document.getElementById('nombreProyecto').value,
      descripcion: document.getElementById('descripcionProyecto').value,
      fecha_inicio: document.getElementById('fechaInicio').value,
      fecha_fin: document.getElementById('fechaFin').value,
      grupo: document.getElementById('grupoProyecto').value
    };

    fetch('/api/proyecto/crear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    })
      .then(resp => resp.json())
      .then(data => {
        if (data.message) {
          alert("✅ " + data.message);
          document.getElementById('formCrearProyecto').reset();
          cargarProyectos();
        } else if (data.error) {
          alert("❌ " + data.error);
        }
      })
      .catch(error => {
        console.error('Error en la creación del proyecto:', error);
        alert("❌ Error inesperado al crear el proyecto");
      });
  });

  cargarProyectos();
}

function cargarProyectos() {
  fetch('/api/proyectos')
    .then(res => res.json())
    .then(data => {
      const tabla = document.getElementById('tablaProyectosBody');
      tabla.innerHTML = '';
      data.forEach(proy => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
          <td>${proy.nombre}</td>
          <td>${proy.descripcion}</td>
          <td>${proy.fecha_inicio}</td>
          <td>${proy.fecha_fin}</td>
          <td>${proy.grupo}</td>
          <td>${proy.estado}</td>
          <td>
            <button class="btn btn-sm btn-primary" onclick="editarProyecto(${proy.id})">Editar</button>
            <button class="btn btn-sm btn-danger" onclick="inactivarProyecto(${proy.id})">Inactivar</button>
          </td>
        `;
        tabla.appendChild(fila);
      });
    });
}

function inactivarProyecto(id) {
  fetch(`/api/proyecto/inactivar/${id}`, { method: 'POST' })
    .then(res => res.json())
    .then(resp => {
      if (resp.message) {
        alert(resp.message);
        cargarProyectos();
      }
    });
}

function editarProyecto(id) {
  fetch(`/api/proyecto/${id}`)
    .then(res => res.json())
    .then(proy => {
      document.getElementById('nombreProyecto').value = proy.nombre;
      document.getElementById('descripcionProyecto').value = proy.descripcion;
      document.getElementById('fechaInicio').value = proy.fecha_inicio;
      document.getElementById('fechaFin').value = proy.fecha_fin;
      document.getElementById('grupoProyecto').value = proy.grupo;

      const btn = document.querySelector('#formCrearProyecto button[type="submit"]');
      btn.textContent = "Actualizar Proyecto";
      btn.classList.remove("btn-success");
      btn.classList.add("btn-warning");

      document.getElementById('formCrearProyecto').onsubmit = function (e) {
        e.preventDefault();
        const data = {
          nombre: document.getElementById('nombreProyecto').value,
          descripcion: document.getElementById('descripcionProyecto').value,
          fecha_inicio: document.getElementById('fechaInicio').value,
          fecha_fin: document.getElementById('fechaFin').value,
          grupo: document.getElementById('grupoProyecto').value
        };

        fetch(`/api/proyecto/editar/${id}`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(data)
        })
        .then(resp => resp.json())
        .then(data => {
          if (data.message) {
            alert("✅ " + data.message);
            document.getElementById('formCrearProyecto').reset();
            btn.textContent = "Crear Proyecto";
            btn.classList.remove("btn-warning");
            btn.classList.add("btn-success");
            cargarProyectos();
          } else {
            alert("❌ " + data.error);
          }
        });
      };
    });
}
window.editarProyecto = editarProyecto;
window.inactivarProyecto = inactivarProyecto;


//Parte de seguimiento de proyectos
if (seguimientoLink) {
  seguimientoLink.addEventListener('click', async e => {
    e.preventDefault();
    ocultarSecciones();

    const proyectos = await obtenerProyectos();

    if (proyectos.length === 0) {
      mainContent.innerHTML = '<p>No hay proyectos registrados.</p>';
      return;
    }

    const modales = proyectos.map((p, i) => `
      <div class="card mb-3 shadow-sm">
        <div class="card-body">
          <h5 class="card-title">${p.nombre}</h5>
          <p class="card-text">${p.descripcion}</p>
          <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#modalProyecto${i}">
            Ver seguimiento
          </button>
        </div>
      </div>

      <div class="modal fade" id="modalProyecto${i}" tabindex="-1" aria-labelledby="modalLabel${i}" aria-hidden="true">
        <div class="modal-dialog modal-lg">
          <div class="modal-content">
            <div class="modal-header">
              <h5 class="modal-title" id="modalLabel${i}">Seguimiento: ${p.nombre}</h5>
              <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Cerrar"></button>
            </div>
            <div class="modal-body">
              <p><strong>Grupo:</strong> ${p.grupo}</p>
              <p><strong>Fecha inicio:</strong> ${p.fecha_inicio}</p>
              <p><strong>Fecha fin:</strong> ${p.fecha_fin}</p>
              <button class="btn btn-success btn-ver-progreso" data-proyecto="${p.nombre}">
                Ver progreso de tareas
              </button>
            </div>
            <div class="modal-footer">
              <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
          </div>
        </div>
      </div>
    `).join('');

    mainContent.innerHTML = `
      <h3 class="mb-4">Seguimiento de Proyectos</h3>
      ${modales}
    `;
  });
}

async function obtenerProyectos() {
  const res = await fetch('/api/proyectos');
  return await res.json();
}

// Delegación para botón "Ver progreso de tareas"
document.addEventListener('click', async function (e) {
  if (e.target.classList.contains('btn-ver-progreso')) {
    const nombreProyecto = e.target.getAttribute('data-proyecto');

    // Cerrar modal si está activo
    const modalesActivos = document.querySelectorAll('.modal.show');
    modalesActivos.forEach(modal => {
      const instance = bootstrap.Modal.getInstance(modal);
      instance.hide();
    });

    const res = await fetch(`/api/proyecto/${nombreProyecto}`);
    const data = await res.json();

    const porcentaje = data.progreso || 0;
    const pendientes = data.pendientes || [];

    const barra = `
      <div class="mb-4">
        <h4>Progreso de Tareas</h4>
        <div class="progress">
          <div class="progress-bar bg-success" role="progressbar"
            style="width: ${porcentaje}%;" aria-valuenow="${porcentaje}" aria-valuemin="0" aria-valuemax="100">
            ${porcentaje}%
          </div>
        </div>
      </div>
    `;

    const listaPendientes = pendientes.length > 0
      ? pendientes.map(t => {
          const nombres = t.no_entregaron.length > 0
            ? `<ul>${t.no_entregaron.map(n => `<li>${n}</li>`).join('')}</ul>`
            : `<p>Todos entregaron.</p>`;
          return `<div class="mb-3"><strong>${t.titulo}</strong> (vence: ${t.fecha_vencimiento})${nombres}</div>`;
        }).join('')
      : '<li>No hay tareas pendientes.</li>';

    const html = `
      <h3 class="mb-3">Progreso del Proyecto: ${nombreProyecto}</h3>
      ${barra}
      <div class="mb-3">
        <h5>Trabajadores con tareas pendientes:</h5>
        ${listaPendientes}
      </div>
      <button class="btn btn-danger" onclick="generarPDF('${nombreProyecto}')">
        Generar PDF de pendientes
      </button>
    `;

    mainContent.innerHTML = html;
  }
});


//Parte de Asignacion de trabajadores
// Detectar clic en el menú lateral: "Asignación"

if (Asignacionlink) {
  Asignacionlink.addEventListener("click", function (e) {
    e.preventDefault();
    ocultarSecciones(); // Oculta otras vistas
    cargarVistaAsignacion(); // Muestra la tabla de asignación
  });
}

// Función que carga la tabla de trabajadores sin grupo
function cargarVistaAsignacion() {
  fetch('/api/trabajadores/sin_grupo')
    .then(res => res.json())
    .then(trabajadores => {
      let html = `
        <h2 class="mb-4">Asignación de Grupos</h2>
        <div class="table-responsive">
          <table class="table table-bordered align-middle text-center">
            <thead class="table-success">
              <tr>
                <th>Nombre del Trabajador</th>
                <th>Grupo</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              ${trabajadores.map(t => `
                <tr data-id="${t.id}">
                  <td>${t.nombre_completo}</td>
                  <td>
                    <select class="form-select grupo-select">
                      <option value="">Seleccione un grupo</option>
                    </select>
                  </td>
                  <td>
                    <button class="btn btn-success btn-asignar">Asignar</button>
                  </td>
                </tr>
              `).join('')}
            </tbody>
          </table>
        </div>
      `;

      document.getElementById("mainContent").innerHTML = html;
      cargarGruposEnSelects(); // Llenar los <select> con grupos activos
    })
    .catch(err => {
      console.error('Error al cargar trabajadores sin grupo:', err);
      document.getElementById("mainContent").innerHTML = "<p>Error al cargar datos.</p>";
    });
}

// Función que llena todos los <select> con los grupos disponibles (según los proyectos activos)
function cargarGruposEnSelects() {
  fetch('/api/proyectos')
    .then(res => res.json())
    .then(proyectos => {
      const selects = document.querySelectorAll('.grupo-select');
      selects.forEach(select => {
        proyectos.forEach(p => {
          const option = document.createElement('option');
          option.value = p.grupo;
          option.textContent = `${p.grupo} - ${p.nombre}`;
          select.appendChild(option);
        });
      });
    })
    .catch(err => {
      console.error('Error al cargar los grupos:', err);
    });
}

// Delegación de eventos: cuando hacen clic en "Asignar"
document.addEventListener('click', function (e) {
  if (e.target.classList.contains('btn-asignar')) {
    const row = e.target.closest('tr');
    const id = row.getAttribute('data-id');
    const grupo = row.querySelector('.grupo-select').value;

    if (!grupo) {
      alert("Por favor seleccione un grupo.");
      return;
    }

    fetch('/api/asignar_grupo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id, grupo })
    })
    .then(res => res.json())
    .then(data => {
      if (data.status === 'success') {
        row.remove(); // Eliminar la fila de la tabla
      } else {
        alert(data.message || "Error al asignar grupo.");
      }
    })
    .catch(err => {
      console.error('Error al enviar asignación:', err);
      alert("Hubo un error al asignar el grupo.");
    });
  }
});

});
// Función para generar el PDF (Es parte de seguimiento de proyectos)
function generarPDF(nombreProyecto) {
  window.open(`/api/proyecto/${encodeURIComponent(nombreProyecto)}/pdf`, '_blank');
}

// --- BOTÓN DE CHAT PRINCIPAL ---
document.getElementById('chat-fab').addEventListener('click', () => {
  document.getElementById('chat-messenger').style.display = 'flex';
  cargarListaChats();
});

document.getElementById('close-chat-messenger').addEventListener('click', () => {
  document.getElementById('chat-messenger').style.display = 'none';
  cerrarChatPopup();
});

// --- FUNCIONES DE CHAT ---
let usuarioChatActual = null;

function cargarListaChats() {
  fetch('/api/lideres/chat')
    .then(res => res.json())
    .then(lideres => {
      const lista = document.getElementById('chat-list');
      lista.innerHTML = '';
      lideres.forEach(l => {
        // Construir la ruta completa de la foto
        const rutaFoto = l.foto && l.foto.trim() !== ''
          ? `/static/avatars/${l.foto}`
          : '/static/avatars/default.png';

        const div = document.createElement('div');
        div.classList.add('chat-list-item');
        div.innerHTML = `
          <img src="${rutaFoto}" class="chat-avatar-mini">
          <div>
            <div><strong>${l.nombre_completo}</strong></div>
            <small>Haz clic para abrir el chat</small>
          </div>`;
        div.onclick = () => abrirChatPopup(l.id, l.nombre_completo, l.foto);
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

  // Construir la ruta completa de la imagen de perfil
  const rutaFoto = foto && foto.trim() !== ''
    ? `/static/avatars/${foto}`
    : '/static/avatars/default.png';

  document.getElementById('chat-avatar').src = rutaFoto;
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
      mensajes.forEach(m => {
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
          div.textContent = `${m.emisor === 'admin' ? 'Tú' : m.emisor}: ${m.mensaje}`;
        }

        contenedor.appendChild(div);
      });
      contenedor.scrollTop = contenedor.scrollHeight;
    });
}

document.getElementById('chat-popup-form').addEventListener('submit', e => {
  e.preventDefault();
  const input = document.getElementById('chat-popup-input');
  const mensaje = input.value.trim();
  if (!mensaje || !usuarioChatActual) return;

  fetch('/api/chat/enviar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ receptor_id: usuarioChatActual, mensaje })
  }).then(() => {
    input.value = '';
    cargarMensajesPopup(usuarioChatActual);
  });
});

document.getElementById('chat-popup-img').addEventListener('change', function () {
  const file = this.files[0];
  if (!file || !usuarioChatActual) return;
  const formData = new FormData();
  formData.append('imagen', file);
  formData.append('receptor_id', usuarioChatActual);

  fetch('/api/chat/enviar-imagen', {
    method: 'POST',
    body: formData
  }).then(() => cargarMensajesPopup(usuarioChatActual));
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
