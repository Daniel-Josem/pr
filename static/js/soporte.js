// soporte.js - Lógica para el formulario de soporte

document.addEventListener('DOMContentLoaded', function() {
  const form = document.getElementById('formulario-soporte');
  if (form) {
    form.addEventListener('submit', async function(e) {
      e.preventDefault();
      const asunto = document.getElementById('asunto-soporte')?.value.trim();
      const tipo = document.getElementById('tipo-soporte')?.value;
      const descripcion = document.getElementById('descripcion-soporte')?.value.trim();
      const mensajeDiv = document.getElementById('mensaje-soporte');
      if (mensajeDiv) mensajeDiv.textContent = '';
      if (!asunto || !tipo || !descripcion) {
        if (mensajeDiv) {
          mensajeDiv.textContent = 'Por favor, completa todos los campos.';
          mensajeDiv.className = 'mt-3 text-danger fw-semibold';
        }
        return;
      }
      try {
        const resp = await fetch('/api/soporte', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ asunto, tipo, descripcion })
        });
        if (mensajeDiv) {
          if (resp.ok) {
            mensajeDiv.textContent = '¡Tu consulta fue enviada correctamente!';
            mensajeDiv.className = 'mt-3 text-success fw-semibold';
            form.reset();
          } else {
            mensajeDiv.textContent = 'Hubo un error al enviar tu consulta. Intenta nuevamente.';
            mensajeDiv.className = 'mt-3 text-danger fw-semibold';
          }
        }
      } catch (err) {
        if (mensajeDiv) {
          mensajeDiv.textContent = 'Error de conexión. Intenta más tarde.';
          mensajeDiv.className = 'mt-3 text-danger fw-semibold';
        }
      }
    });
  }
});
