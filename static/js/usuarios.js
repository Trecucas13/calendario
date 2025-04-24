document.addEventListener("DOMContentLoaded", function () {
    // Inicializar el estado de la navbar
    initNavbarState();
  
    // Obtener el input de búsqueda
    const searchInput = document.getElementById("busqueda");
  
    // Obtener la tabla
    const tabla = document.querySelector("table");
  
    /**
     * Elimina las tildes de un texto
     * @param {string} texto - Texto del que se eliminarán las tildes
     * @returns {string} - Texto sin tildes
     */
    function eliminarTildes(texto) {
      return texto.normalize("NFD")
        .replace(/[\u0300-\u036f]/g, "")
        .toLowerCase();
    }
  
    /**
     * Busca texto en todas las celdas de la tabla y muestra/oculta filas según coincidencias
     * @param {string} textoBusqueda - Texto a buscar en la tabla
     */
    function buscarEnTabla(textoBusqueda) {
      // Eliminar tildes del texto de búsqueda
      const textoBusquedaSinTildes = eliminarTildes(textoBusqueda);
  
      // Obtener todas las filas del tbody, excluyendo el encabezado
      const filas = tabla.querySelectorAll("tbody tr");
  
      filas.forEach((fila) => {
        // Flag para determinar si se muestra la fila
        let mostrarFila = false;
  
        // Obtener todas las celdas de la fila
        const celdas = fila.querySelectorAll("td");
  
        // Recorrer todas las celdas
        celdas.forEach((celda) => {
          // Eliminar tildes del texto de la celda
          const textoCeldaSinTildes = eliminarTildes(celda.textContent);
  
          if (textoCeldaSinTildes.includes(textoBusquedaSinTildes)) {
            mostrarFila = true;
          }
        });
  
        // Mostrar u ocultar fila según resultado
        fila.style.display = mostrarFila ? "" : "none";
      });
    }
  
    // Configurar evento de búsqueda en tiempo real
    if (searchInput) {
      searchInput.addEventListener("input", function () {
        buscarEnTabla(this.value);
      });
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
    // Tooltips
    const tooltips = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'))
        .map(tooltipEl => new bootstrap.Tooltip(tooltipEl))

    // Eliminación con confirmación
    const deleteModal = document.getElementById('confirmDeleteModal')
    deleteModal.addEventListener('show.bs.modal', event => {
        const button = event.relatedTarget
        const userId = button.getAttribute('data-user-id')
        const form = document.getElementById('deleteForm')
        form.action = `/eliminar_usuario/${userId}`
    })
})