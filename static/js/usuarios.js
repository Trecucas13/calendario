// Función para mostrar el modal de actualización de datos
function mostrarModalActualizarDatos(id) {
  // Obtener el modal
  const modal = document.getElementById("modalActualizarDatos");

  // Establecer el ID en el campo oculto
  document.getElementById("id").value = id;

  // Obtener los datos del usuario mediante AJAX
  fetch(`/obtener_usuario/${id}`)
    .then((response) => response.json())
    .then((data) => {
      // Llenar los campos del formulario con los datos del usuario
      document.getElementById("actualizarDocumento").value = data.documento;
      document.getElementById("actualizarNombre").value = data.nombre;
      document.getElementById("actualizarRol").value = data.rol;

      // Mostrar el modal
      modal.style.display = "block";
    })
    .catch((error) => {
      console.error("Error al obtener datos del usuario:", error);
      alert("Error al obtener datos del usuario");
    });
}

// Función para cerrar el modal
function cerrarModal(modalId) {
  const modal = document.getElementById(modalId);
  modal.style.display = "none";
}

// Función para eliminar un usuario
function eliminar_usuario(id) {
  try {
    const modal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    
    // Obtener el campo oculto específico para eliminación
    const idField = document.getElementById('deleteUserId');
    
    if (!idField) {
        throw new Error('Campo oculto deleteUserId no encontrado');
    }
    
    // Asignar el ID directamente desde el parámetro
    idField.value = id;
    modal.show();
  } catch (error) {
    console.error('Error en eliminación:', error);
    alert('Error al procesar solicitud');
  }
}

// Configurar listener único al cargar la página
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('[data-user-id-delete]').forEach(button => {
        button.addEventListener('click', function() {
            const userId = this.getAttribute('data-user-id-delete');
            eliminar_usuario(userId);
        });
    });
});

// Cerrar modales cuando se hace clic fuera de ellos
window.onclick = function (event) {
  const modales = document.getElementsByClassName("modal");
  for (let i = 0; i < modales.length; i++) {
    if (event.target == modales[i]) {
      cerrarModal(modales[i].id);
    }
  }
};

// Función para realizar la búsqueda en la tabla
function buscarUsuarios() {
  try {
    const searchText = document
      .getElementById("busqueda")
      .value.toLowerCase()
      .trim();
    const table = document.getElementById("tablaUsuarios");

    if (!table) {
      console.error("No se encontró la tabla de usuarios");
      return;
    }

    const tbody = table.querySelector("tbody");
    if (!tbody) {
      console.error("No se encontró el tbody en la tabla");
      return;
    }

    const rows = tbody.querySelectorAll("tr");

    rows.forEach((row) => {
      const cells = row.querySelectorAll("td");
      let shouldShow = searchText === "" ? true : false;

      cells.forEach((cell) => {
        const content = cell.textContent || cell.innerText;
        if (content.toLowerCase().indexOf(searchText) > -1) {
          shouldShow = true;
        }
      });

      row.style.display = shouldShow ? "" : "none";
    });
  } catch (error) {
    console.error("Error en la búsqueda:", error);
  }
}

// Inicializar eventos de búsqueda
document.addEventListener("DOMContentLoaded", function () {
  try {
    // Configurar el campo de búsqueda
    const campoBusqueda = document.getElementById("busqueda");
    if (campoBusqueda) {
      ["input", "keyup", "change"].forEach((evento) => {
        campoBusqueda.addEventListener(evento, buscarUsuarios);
      });
    }

    // Configurar el botón de búsqueda
    const botonBusqueda = document.getElementById("boton-busqueda");
    if (botonBusqueda) {
      botonBusqueda.addEventListener("click", buscarUsuarios);
    }

    // Ejecutar una búsqueda inicial
    buscarUsuarios();
  } catch (error) {
    console.error("Error al inicializar la búsqueda:", error);
  }
});
