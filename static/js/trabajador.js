// --- SOCKET.IO para mensajes en tiempo real ---
if (typeof io !== 'undefined') {
  const socket = io();
  
  // Escuchar nuevos mensajes
  socket.on('nuevo_mensaje', function(msg) {
    // Si estamos en un chat con el líder que envió el mensaje, mostrar el mensaje
    if (selectedLiderId && msg.emisor_id == selectedLiderId) {
      cargarMensajes(selectedLiderId);
    }
  });
  
  // Hacer el socket disponible globalmente
  window.socket = socket;
}

// Función para sincronizar mensajes periódicamente (respaldo)
function sincronizarMensajes() {
  if (selectedLiderId) {
    cargarMensajes(selectedLiderId);
  }
}

// Actualizar mensajes cada 5 segundos como respaldo
setInterval(sincronizarMensajes, 5000);

// Chatbox para trabajador: enviar mensajes solo a líderes

document.addEventListener('DOMContentLoaded', function () {
  const chatUserList = document.getElementById('chatUserList');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  let selectedLiderId = null;


  // Cargar lista de líderes del mismo grupo
  fetch('/api/chat/lideres')
    .then(res => res.json())
    .then(lideres => {
      chatUserList.innerHTML = '';
      lideres.forEach(l => {
        const li = document.createElement('li');
        li.innerHTML = `${l.nombre_completo} <span class="badge bg-primary ms-2">Líder</span>`;
        li.dataset.id = l.id;
        li.onclick = () => seleccionarUsuario(l.id, l.nombre_completo, l.rol);
        chatUserList.appendChild(li);
      });
    });

  function seleccionarUsuario(id, nombre, rol) {
    selectedLiderId = id;
    document.getElementById('chatWith').textContent = nombre + ' (Líder)';
    cargarMensajes(id);
  }


  function cargarMensajes(usuarioId) {
    fetch(`/api/chat/${usuarioId}`)
      .then(res => res.json())
      .then(mensajes => {
        chatMessages.innerHTML = '';
        mensajes.forEach(m => {
          const div = document.createElement('div');
          div.className = m.emisor_id === usuarioId ? 'mensaje-lider' : 'mensaje-trabajador';
          div.innerHTML = `<strong>${m.emisor_nombre}:</strong> ${m.mensaje}`;
          chatMessages.appendChild(div);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
  }


  chatSendBtn.onclick = function () {
    if (!selectedLiderId || !chatInput.value.trim()) return;
    
    const mensaje = chatInput.value.trim();
    
    // Usar Socket.IO para enviar mensaje en tiempo real
    if (typeof socket !== 'undefined') {
      socket.emit('enviar_mensaje', {
        receptor_id: selectedLiderId,
        mensaje: mensaje,
        tipo: 'texto'
      });
      chatInput.value = '';
    } else {
      // Fallback a HTTP si Socket.IO no está disponible
      fetch('/api/chat/enviar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ receptor_id: selectedLiderId, mensaje: mensaje })
      })
        .then(res => res.json())
        .then(resp => {
          if (resp.success) {
            cargarMensajes(selectedLiderId);
            chatInput.value = '';
          }
        });
    }
  };
});
document.getElementById('archivo').addEventListener('change', function () {
      const archivo = this.files[0];

      if (archivo) {
          const tamañoMaximo = 5 * 1024 * 1024; // 5 MB
          const tamañoMinimo = 10 * 1024;       // 10 KB

          if (archivo.size > tamañoMaximo) {
              alert('El archivo supera el límite máximo de 5 MB.');
              this.value = '';
          } else if (archivo.size < tamañoMinimo) {
              alert('El archivo es demasiado pequeño. El mínimo permitido es 10 KB.');
              this.value = '';
          }
      }
  });