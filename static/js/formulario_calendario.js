    // Mostrar/ocultar opciones de tiempo fuera
    document.querySelectorAll('input[name="tiempoFuera"]').forEach(radio => {
        radio.addEventListener('change', function() {
          const tiempoFueraOptions = document.getElementById('tiempoFueraOptions');
          if (this.value === 'si') {
            tiempoFueraOptions.classList.remove('hidden');
          } else {
            tiempoFueraOptions.classList.add('hidden');
          }
        });
      });
      
      // Validar fechas
      document.getElementById('calendarioForm').addEventListener('submit', function(event) {
        const fechaInicio = new Date(document.getElementById('fechaInicio').value);
        const fechaFin = new Date(document.getElementById('fechaFin').value);
        
        if (fechaFin < fechaInicio) {
          alert('La fecha de fin debe ser posterior a la fecha de inicio');
          event.preventDefault();
        }
      });

//ACTUALIZAR CALENDARIO
//FUNCIONAMIENTO DEL BOTÓN PARA ACTUALIZAR

//TRAER LA INFORMACIÓN AL CALENDARIO

// ... existing code ...

// Función para cargar los datos del calendario en el formulario de actualización
function cargarDatosCalendario(id) {
  fetch(`/obtener_calendario/${id}`)
      .then(response => {
          if (!response.ok) {
              throw new Error('No se pudo obtener los datos del calendario');
          }
          return response.json();
      })
      .then(data => {
          // Llenar los campos del formulario con los datos obtenidos
          document.getElementById('titulo').value = data.titulo;
          document.getElementById('fecha_inicio').value = data.fecha_inicio;
          document.getElementById('fecha_fin').value = data.fecha_fin;
          document.getElementById('descripcion').value = data.descripcion;
          // Llenar más campos según sea necesario
          
          // Guardar el ID para usarlo en la actualización
          document.getElementById('calendario_id').value = data.id;
      })
      .catch(error => {
          console.error('Error:', error);
          alert('Error al cargar los datos del calendario');
      });
}

// Detectar cuando se abre el formulario de actualización
document.addEventListener('DOMContentLoaded', function() {
  // Verificar si estamos en la página de actualización
  const urlParams = new URLSearchParams(window.location.search);
  const calendarioId = urlParams.get('id');
  
  if (calendarioId) {
      // Si hay un ID en la URL, cargar los datos
      cargarDatosCalendario(calendarioId);
  }
});

// ... existing code ...

//