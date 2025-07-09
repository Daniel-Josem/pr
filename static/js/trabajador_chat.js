// Chatbox para trabajador: solo ve y escribe a su líder asignado

document.addEventListener('DOMContentLoaded', function () {
  const chatUserList = document.getElementById('chatUserList');
  const chatMessages = document.getElementById('chatMessages');
  const chatInput = document.getElementById('chatInput');
  const chatSendBtn = document.getElementById('chatSendBtn');
  let selectedLiderId = null;

  // Obtener el ID del usuario logueado desde un atributo data o variable global
  let usuarioActualId = null;
  if (window.usuarioActualId) {
    usuarioActualId = window.usuarioActualId;
  } else if (chatUserList && chatUserList.dataset.userid) {
    usuarioActualId = chatUserList.dataset.userid;
  } else if (window.usuario_id) {
    usuarioActualId = window.usuario_id;
  }

  // Cargar el líder asignado
  fetch('/api/usuarios/chat')
    .then(res => res.json())
    .then(lideres => {
      chatUserList.innerHTML = '';
      if (lideres.length > 0) {
        const l = lideres[0];
        selectedLiderId = l.id;
        const li = document.createElement('li');
        li.textContent = l.nombre_completo;
        li.dataset.id = l.id;
        li.onclick = () => seleccionarLider(l.id, l.nombre_completo);
        chatUserList.appendChild(li);
        seleccionarLider(l.id, l.nombre_completo);
      } else {
        chatUserList.innerHTML = '<li>No tienes líder asignado</li>';
      }
    });

  function seleccionarLider(id, nombre) {
    selectedLiderId = id;
    document.getElementById('chatWith').textContent = nombre;
    cargarMensajes(id);
  }

  function cargarMensajes(liderId) {
    fetch(`/api/chat/${liderId}`)
      .then(res => res.json())
      .then(mensajes => {
        chatMessages.innerHTML = '';
        mensajes.forEach(m => {
          const div = document.createElement('div');
          div.className = m.emisor_rol === 'lider' ? 'mensaje-lider' : 'mensaje-trabajador';
          div.innerHTML = `<b>${m.emisor_nombre}</b> <span class='fecha-msg'>${(m.fecha||'').replace('T',' ').slice(0,16)}</span><br>${m.mensaje}`;
          chatMessages.appendChild(div);
        });
        chatMessages.scrollTop = chatMessages.scrollHeight;
      });
  }

  chatSendBtn.onclick = function () {
    if (!selectedLiderId || !chatInput.value.trim()) return;
    fetch('/api/chat/enviar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ receptor_id: selectedLiderId, mensaje: chatInput.value })
    })
      .then(res => res.json())
      .then(resp => {
        if (resp.success) {
          cargarMensajes(selectedLiderId);
          chatInput.value = '';
        }
      });
  };

  // Socket.IO: Recibir mensajes en tiempo real
  if (typeof io !== 'undefined') {
    const socket = io();
    socket.on('nuevo_mensaje', function(msg) {
      // Si el mensaje es para el trabajador logueado o para su chat abierto
      if ((msg.receptor_id == usuarioActualId || msg.emisor_id == usuarioActualId) &&
          (msg.receptor_id == selectedLiderId || msg.emisor_id == selectedLiderId)) {
        cargarMensajes(selectedLiderId);
      }
    });
  }

  // Refrescar mensajes cada 5s (opcional)
  setInterval(() => {
    if (selectedLiderId) cargarMensajes(selectedLiderId);
  }, 5000);
});
