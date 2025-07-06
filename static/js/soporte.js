document.addEventListener('DOMContentLoaded', function() {
// soporte.js - Lógica para el formulario de soporte

const form = document.getElementById('formulario-soporte');
if (form) {
  form.addEventListener('submit', async function(e) {
    e.preventDefault();
    const asunto = document.getElementById('asunto-soporte')?.value.trim();
    const tipo = document.getElementById('tipo-soporte')?.value;
    const descripcion = document.getElementById('descripcion-soporte')?.value.trim();
    const mensajeDiv = document.getElementById('mensaje-soporte');
    if (mensajeDiv) mensajeDiv.textContent = '';
    
    if (!asunto || !descripcion) {
      if (mensajeDiv) {
        mensajeDiv.textContent = 'Por favor, completa Asunto y Descripción.';
        mensajeDiv.className = 'mt-3 text-danger fw-semibold';
      }
      return;
    }
    
    // Mostrar mensaje de envío
    if (mensajeDiv) {
      mensajeDiv.textContent = 'Enviando reporte...';
      mensajeDiv.className = 'mt-3 text-info fw-semibold';
    }
    
    try {
      // Enviar usando la ruta del trabajador
      const formData = new FormData(form);
      const resp = await fetch('/enviar_reporte', {
        method: 'POST',
        body: formData,
        credentials: 'include' // Enviar cookies de sesión
      });
      
      const data = await resp.json();
      if (data.ok) {
        if (mensajeDiv) {
          mensajeDiv.textContent = '¡Tu consulta fue enviada correctamente!';
          mensajeDiv.className = 'mt-3 text-success fw-semibold';
          form.reset();
        }
      } else {
        if (mensajeDiv) {
          mensajeDiv.textContent = data.error || 'Hubo un error al enviar tu consulta.';
          mensajeDiv.className = 'mt-3 text-danger fw-semibold';
        }
      }
    } catch (err) {
      console.error('Error:', err);
      if (mensajeDiv) {
        mensajeDiv.textContent = 'Error de conexión. Intenta más tarde.';
        mensajeDiv.className = 'mt-3 text-danger fw-semibold';
      }
    }
  });
}
});
