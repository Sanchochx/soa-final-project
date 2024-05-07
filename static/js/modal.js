// modal.js

// Función para abrir el modal de confirmación de eliminación
function confirmarEliminacion(usuario_id) {
    var modal = document.getElementById('confirmarEliminacionModal');
    modal.style.display = 'block';

    // Configurar el formulario de eliminación para enviar el usuario_id
    var form = document.getElementById('eliminarUsuarioForm');
    form.action = '/eliminar_usuario/' + usuario_id;
}


// Función para cerrar el modal
function cerrarModal() {
    var modals = document.getElementsByClassName('modal');
    for (var i = 0; i < modals.length; i++) {
        modals[i].style.display = 'none';
    }
}

// Cerrar el modal si el usuario hace clic fuera de él
window.onclick = function(event) {
    var modals = document.getElementsByClassName('modal');
    for (var i = 0; i < modals.length; i++) {
        if (event.target == modals[i]) {
            modals[i].style.display = 'none';
        }
    }
}
