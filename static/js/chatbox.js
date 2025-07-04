// chatbox.js - Mostrar/ocultar chatbox flotante

document.addEventListener('DOMContentLoaded', function() {
  const chatbox = document.getElementById('chatbox');
  const toggleBtn = document.getElementById('chatbox-toggle-btn');
  const closeBtn = document.getElementById('chatbox-close-btn');
  if (toggleBtn && chatbox) {
    toggleBtn.addEventListener('click', function() {
      chatbox.style.display = 'block';
      toggleBtn.style.display = 'none';
    });
  }
  if (closeBtn && chatbox && toggleBtn) {
    closeBtn.addEventListener('click', function() {
      chatbox.style.display = 'none';
      toggleBtn.style.display = 'flex';
    });
  }
});
