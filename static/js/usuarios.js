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
// Function to handle user deletion


// Configurar listener único al cargar la página
// Agregar event listeners cuando el DOM esté completamente cargado
document.addEventListener('DOMContentLoaded', function() {
  // Configurar los botones de eliminación
  const deleteButtons = document.querySelectorAll('[data-bs-target="#confirmDeleteModal"]');
  deleteButtons.forEach(button => {
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
    
    // Configurar el modal de eliminación
    const deleteModal = document.getElementById('confirmDeleteModal');
    if (deleteModal) {
      deleteModal.addEventListener('show.bs.modal', function(event) {
        // Este evento se dispara automáticamente por Bootstrap
        // y puede servir como respaldo si el onclick falla
        const button = event.relatedTarget;
        if (button) {
          const userId = button.getAttribute('data-user-id-delete');
          if (userId) {
            console.log('ID capturado desde evento modal:', userId);
            const idField = document.getElementById('deleteUserId');
            if (idField) {
              idField.value = userId;
              
              // Opcional: mostrar el ID en el cuerpo del modal
              const userIdDisplay = document.getElementById('userIdDisplay');
              if (userIdDisplay) {
                userIdDisplay.textContent = '(ID: ' + userId + ')';
              }
            }
          } else {
            console.warn('No se encontró data-user-id-delete en el botón');
          }
        } else {
          console.warn('No se pudo obtener el botón que activó el modal');
        }
      });
    }
    
    // Asegurarse de que el formulario de eliminación tenga el ID correcto al enviar
    const deleteForm = document.getElementById('deleteUserForm');
    if (deleteForm) {
      deleteForm.addEventListener('submit', function(event) {
        const idField = document.getElementById('deleteUserId');
        if (!idField || !idField.value) {
          event.preventDefault();
          console.error('No hay ID de usuario para eliminar');
          alert('Error: No se pudo identificar el usuario a eliminar');
        } else {
          console.log('Enviando formulario para eliminar usuario ID:', idField.value);
        }
      });
    }
  } catch (error) {
    console.error("Error al inicializar eventos:", error);
  }
});

// Agregar un evento para cuando el modal se muestre
document.addEventListener('DOMContentLoaded', function() {
  const deleteModal = document.getElementById('confirmDeleteModal');
  if (deleteModal) {
    deleteModal.addEventListener('show.bs.modal', function(event) {
      // Obtener el botón que activó el modal
      const button = event.relatedTarget;
      
      // Extraer el ID del usuario del atributo data
      const userId = button.getAttribute('data-user-id-delete');
      
      // Actualizar el campo oculto con el ID
      const idField = document.getElementById('deleteUserId');
      if (idField && userId) {
        idField.value = userId;
        
        // Opcional: mostrar el ID en el cuerpo del modal para verificación
        const userIdDisplay = document.getElementById('userIdDisplay');
        if (userIdDisplay) {
          userIdDisplay.textContent = '(ID: ' + userId + ')';
        }
        
        console.log('ID asignado desde evento modal:', userId);
      }
    });
  }
});
