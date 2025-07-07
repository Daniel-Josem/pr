console.log('informes.js cargado correctamente');

document.addEventListener('DOMContentLoaded', function () {
    const btnInforme = document.getElementById('informe-link');
    const btnDashboard = document.getElementById('dashboard-link');
    const btnProyecto = document.getElementById('proyecto-link');
    const btnCalendario = document.getElementById('calendario-link');
    const btnBackToTasks = document.getElementById('btnBackToTasks');
    const btnBackToTasksFromProjects = document.getElementById('btnBackToTasksFromProjects');

    const tasksContainer = document.getElementById('tasksContainer');
    const studentsContainer = document.getElementById('studentsContainer');
    const projectsContainer = document.getElementById('projectsContainer');
    const calendarioContainer = document.getElementById('contenido-calendario');
    const informeContainer = document.getElementById('informeContainer');

    function ocultarTodo() {
        if (tasksContainer) tasksContainer.style.display = 'none';
        if (studentsContainer) studentsContainer.style.display = 'none';
        if (projectsContainer) projectsContainer.style.display = 'none';
        if (calendarioContainer) calendarioContainer.style.display = 'none';
        if (informeContainer) informeContainer.style.display = 'none';
    }

    btnDashboard.addEventListener('click', function (e) {
        e.preventDefault();
        ocultarTodo();
        tasksContainer.style.display = 'block';
    });

    btnProyecto.addEventListener('click', function (e) {
        e.preventDefault();
        ocultarTodo();
        projectsContainer.style.display = 'block';
    });

    btnCalendario.addEventListener('click', function (e) {
        e.preventDefault();
        ocultarTodo();
        calendarioContainer.style.display = 'block';
        cargarCalendario();
    });

    btnInforme.addEventListener('click', function (e) {
        e.preventDefault();
        ocultarTodo();
        informeContainer.style.display = 'block';
    });

    btnBackToTasks.addEventListener('click', function () {
        ocultarTodo();
        tasksContainer.style.display = 'block';
    });

    btnBackToTasksFromProjects.addEventListener('click', function () {
        ocultarTodo();
        tasksContainer.style.display = 'block';
    });

    // Navegación por grupos (estudiantes)
    document.querySelectorAll('.curso-link-sidebar').forEach(function (grupoLink) {
        grupoLink.addEventListener('click', function (e) {
            e.preventDefault();
            const grupoNombre = this.textContent.trim();
            document.getElementById('studentsCourseTitle').querySelector('span').textContent = grupoNombre;
            ocultarTodo();
            studentsContainer.style.display = 'block';
        });
    });

    // Botón para descargar informe
    const btnDescargar = document.getElementById('btnDescargarInforme');
    if (btnDescargar) {
        btnDescargar.addEventListener('click', function () {
            window.location.href = '/descargar_informe';
        });
    }
});
