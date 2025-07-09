
// --- CHATBOX UNIFICADO PARA TODOS LOS ROLES ---

// Mostrar error amigable en el chatbox (debe estar antes de cualquier uso)
function mostrarErrorChatbox(mensaje) {
  const contenedor = document.getElementById('chat-popup-mensajes');
  if (!contenedor) return;
  const div = document.createElement('div');
  div.classList.add('chatbox-error-msg');
  div.style.color = '#fff';
  div.style.background = '#d9534f';
  div.style.padding = '10px';
  div.style.margin = '10px';
  div.style.borderRadius = '8px';
  div.style.textAlign = 'center';
  div.textContent = mensaje;
  contenedor.innerHTML = '';
  contenedor.appendChild(div);
}
let socket;
let usuarioChatActual = null;
let usuarioActualId = null;
let usuarioRol = null;

document.addEventListener('DOMContentLoaded', function() {
  // Obtener el id y rol del usuario actual desde variable global o atributo data
  if (window.usuarioActualId) {
    usuarioActualId = window.usuarioActualId;
  } else {
    const chatContainer = document.getElementById('chat-messenger') || document.getElementById('chatbox');
    if (chatContainer && chatContainer.dataset && chatContainer.dataset.usuarioId) {
      usuarioActualId = chatContainer.dataset.usuarioId;
    }
  }
  if (window.usuarioRol) {
    usuarioRol = window.usuarioRol;
  } else {
    const chatContainer = document.getElementById('chat-messenger') || document.getElementById('chatbox');
    if (chatContainer && chatContainer.dataset && chatContainer.dataset.rol) {
      usuarioRol = chatContainer.dataset.rol;
    }
  }

  // Conexión SocketIO
  if (typeof io !== 'undefined') {
    socket = io();
    socket.on('nuevo_mensaje', function(msg) {
      // Si el chat popup está abierto y es el chat correcto, mostrar el mensaje
      if (usuarioChatActual && (msg.emisor_id == usuarioChatActual || msg.emisor_id == usuarioActualId || msg.receptor_id == usuarioActualId)) {
        agregarMensajeAlPopup(msg);
      }
    });
  }

  // --- CHATBOX PARA TODOS LOS ROLES ---
  const chatMessenger = document.getElementById('chat-messenger');
  const fab = document.getElementById('chat-fab');
  const chatForm = document.getElementById('chat-popup-form');
  const chatImg = document.getElementById('chat-popup-img');
  const minimizarBtn = document.getElementById('minimizar-chat-popup');
  const closeMessenger = document.getElementById('close-chat-messenger');

  // FAB: comportamiento según rol
  if (fab) {
    fab.addEventListener('click', function () {
      if (usuarioRol === 'trabajador') {
        // Trabajador: abrir chat directo con líder
        fetch('/api/usuarios/chat')
          .then(res => res.json())
          .then(usuarios => {
            if (usuarios.length > 0) {
              const lider = usuarios[0];
              abrirChatPopup(lider.id, lider.nombre_completo, lider.foto, lider.rol);
            } else {
              alert('No se encontró líder asignado a tu grupo.');
            }
          });
      } else {
        // Admin/líder: mostrar lista de chats
        if (chatMessenger) {
          cargarListaChats();
          chatMessenger.style.display = 'flex';
        }
      }
    });
  }

  // Cerrar Messenger
  if (closeMessenger && chatMessenger) {
    closeMessenger.addEventListener('click', function () {
      chatMessenger.style.display = 'none';
    });
  }

  // Minimizar chat popup
  if (minimizarBtn) {
    minimizarBtn.addEventListener('click', function () {
      document.getElementById('chat-popup').style.display = 'none';
      if (usuarioRol !== 'trabajador' && chatMessenger) chatMessenger.style.display = 'flex';
    });
  }

  // Enviar mensaje texto
  if (chatForm) {
    chatForm.addEventListener('submit', function (e) {
      e.preventDefault();
      enviarMensaje();
    });
  }

  // Enviar imagen
  if (chatImg) {
    chatImg.addEventListener('change', function () {
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
  }
});

// Cargar lista de chats (admin/líder)
function cargarListaChats() {
  fetch('/api/usuarios/chat')
    .then(async res => {
      let usuarios;
      try {
        usuarios = await res.json();
      } catch (e) {
        mostrarErrorChatbox('Sesión expirada o error de autenticación. Por favor, recarga la página o inicia sesión de nuevo.');
        return [];
      }
      return usuarios;
    })
    .then(usuarios => {
      if (!usuarios || !Array.isArray(usuarios)) return;
      const lista = document.getElementById('chat-list');
      if (!lista) return;
      lista.innerHTML = '';
      usuarios.forEach(u => {
        const rutaFoto = u.foto && u.foto.trim() !== ''
          ? `/static/avatars/${u.foto}`
          : '/static/avatars/default.png';
        const div = document.createElement('div');
        div.classList.add('chat-list-item');
        div.innerHTML = `
          <img src="${rutaFoto}" class="chat-avatar-mini">
          <div>
            <div><strong>${u.nombre_completo}</strong> <span class="badge bg-secondary ms-1">${u.rol}</span></div>
            <small>Haz clic para abrir el chat</small>
          </div>`;
        div.onclick = () => abrirChatPopup(u.id, u.nombre_completo, u.foto, u.rol);
        lista.appendChild(div);
      });
    })
    .catch(err => mostrarErrorChatbox('Error cargando lista de chats. Intenta recargar la página.'));
}
window.cargarListaChats = cargarListaChats;

// Abrir popup de chat
function abrirChatPopup(id, nombre, foto, rol) {
  usuarioChatActual = id;
  const chatMessenger = document.getElementById('chat-messenger');
  if (chatMessenger) chatMessenger.style.display = 'none';
  document.getElementById('chat-popup').style.display = 'flex';
  document.getElementById('chat-nombre').textContent = nombre + (rol ? ` (${rol})` : '');
  const rutaFoto = foto && foto.trim() !== ''
    ? `/static/avatars/${foto}`
    : '/static/avatars/default.png';
  document.getElementById('chat-avatar').src = rutaFoto;
  cargarMensajesPopup(id);
}
window.abrirChatPopup = abrirChatPopup;

// Cerrar popup de chat
function cerrarChatPopup() {
  document.getElementById('chat-popup').style.display = 'none';
  document.getElementById('chat-popup-mensajes').innerHTML = '';
  usuarioChatActual = null;
}
window.cerrarChatPopup = cerrarChatPopup;

// Cargar mensajes del chat
function cargarMensajesPopup(receptorId) {
  fetch(`/api/chat/${receptorId}`)
    .then(async res => {
      let mensajes;
      try {
        mensajes = await res.json();
      } catch (e) {
        mostrarErrorChatbox('Sesión expirada o error de autenticación. Por favor, recarga la página o inicia sesión de nuevo.');
        return [];
      }
      return mensajes;
    })
    .then(mensajes => {
      const contenedor = document.getElementById('chat-popup-mensajes');
      if (!contenedor) return;
      contenedor.innerHTML = '';
      if (!mensajes || !Array.isArray(mensajes)) return;
      mensajes.forEach(m => agregarMensajeAlPopup(m));
      contenedor.scrollTop = contenedor.scrollHeight;
    })
    .catch(err => mostrarErrorChatbox('Error cargando mensajes del chat. Intenta recargar la página.'));
}
window.cargarMensajesPopup = cargarMensajesPopup;

// Agregar mensaje al popup
function agregarMensajeAlPopup(m) {
  const contenedor = document.getElementById('chat-popup-mensajes');
  if (!contenedor) return;
  const div = document.createElement('div');
  div.classList.add('chat-bubble');
  if (usuarioActualId && m.emisor_id == usuarioActualId) {
    div.classList.add('chat-bubble-sent');
  } else {
    div.classList.add('chat-bubble-received');
  }
  if (m.tipo === 'imagen') {
    const img = document.createElement('img');
    img.src = m.imagen_url;
    img.classList.add('chat-img-click');
    img.onclick = () => mostrarImagenGrande(img.src);
    div.innerHTML = '';
    div.appendChild(img);
  } else {
    div.innerHTML = `<span class="chat-nombre-emisor">${m.emisor_nombre || m.emisor}${m.emisor_rol ? ` (${m.emisor_rol})` : ''}:</span> ${m.mensaje}`;
  }
  contenedor.appendChild(div);
  contenedor.scrollTop = contenedor.scrollHeight;
}

// Enviar mensaje texto
function enviarMensaje() {
  const input = document.getElementById('chat-popup-input');
  const mensaje = input.value.trim();
  if (!mensaje || !usuarioChatActual) return;
  
  // Usar Socket.IO si está disponible
  if (window.socket) {
    window.socket.emit('enviar_mensaje', {
      receptor_id: usuarioChatActual,
      mensaje: mensaje,
      tipo: 'texto'
    });
    input.value = '';
  } else {
    // Fallback a HTTP
    fetch('/api/chat/enviar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receptor_id: usuarioChatActual, mensaje })
    })
      .then(async res => {
        try {
          await res.json(); // Si la respuesta no es JSON válido, lanzará error
        } catch (e) {
          mostrarErrorChatbox('Sesión expirada o error de autenticación. Por favor, recarga la página o inicia sesión de nuevo.');
          return;
        }
        input.value = '';
        cargarMensajesPopup(usuarioChatActual);
      })
      .catch(err => mostrarErrorChatbox('Error enviando mensaje. Intenta recargar la página.'));
  }
}
window.enviarMensaje = enviarMensaje;

// Mostrar imagen grande
function mostrarImagenGrande(src) {
  window.open(src, '_blank');
}
