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



//