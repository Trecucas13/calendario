// // Función para convertir día de la semana a fecha
// function obtenerFecha(diaSemana) {
//   // Obtener la fecha actual
//   const hoy = new Date();
  
//   // Mapear nombres de días a números (0 = domingo, 1 = lunes, etc.)
//   const diasSemana = {
//     'lunes': 1,
//     'martes': 2,
//     'miercoles': 3,
//     'jueves': 4,
//     'viernes': 5,
//     'sabado': 6,
//     'domingo': 0
//   };
  
//   // Obtener el número del día actual
//   const diaActual = hoy.getDay(); // 0-6
  
//   // Calcular la diferencia de días
//   let diferencia = diasSemana[diaSemana.toLowerCase()] - diaActual;
  
//   // Si la diferencia es negativa, sumamos 7 para obtener el próximo día de la semana
//   if (diferencia < 0) {
//     diferencia += 7;
//   }
  
//   // Crear nueva fecha sumando la diferencia
//   const fecha = new Date(hoy);
//   fecha.setDate(hoy.getDate() + diferencia);
  
//   // Formatear fecha como YYYY-MM-DD para el input
//   return fecha.toISOString().split('T')[0];
// }

// // Función para actualizar el contador
// function actualizarContador(segundos) {
//   const minutos = Math.floor(segundos / 60);
//   const segs = segundos % 60;
//   document.getElementById('contador').textContent = `${minutos}:${segs < 10 ? '0' : ''}${segs}`;
// }

// // Función para validar el formulario
// function validarFormulario() {
//   const tipoDocumento = document.getElementById('tipo-documento').value;
//   const numeroDocumento = document.getElementById('numero-documento').value;
//   const telefono = document.getElementById('telefono').value;
//   const direccion = document.getElementById('direccion').value;
//   const fechaNacimiento = document.getElementById('fecha-nacimiento').value;
//   const examen = document.getElementById('examen').value;
  
//   if (!tipoDocumento || !numeroDocumento || !telefono || !direccion || !fechaNacimiento || !examen) {
//     alert('Por favor complete todos los campos del formulario');
//     return false;
//   }
  
//   return true;
// }

// // Función para verificar si una celda tiene cita
// function verificarCitaExistente(fecha, hora, citas) {
//   if (!citas || citas.length === 0) return false;
  
//   return citas.some(cita => {
//     const citaFecha = cita.fecha ? cita.fecha.toString() : '';
//     const citaHora = cita.hora ? cita.hora.toString() : '';
//     return citaFecha === fecha && citaHora === hora;
//   });
// }

// // Inicializar el estado de las celdas cuando se carga la página
// document.addEventListener('DOMContentLoaded', function() {
//   // Obtener todas las celdas del calendario
//   const celdasCalendario = document.querySelectorAll('.calendario-cell');
  
//   // Para cada celda, verificar su estado
//   celdasCalendario.forEach(celda => {
//     // Si ya tiene una clase de estado, respetarla
//     if (celda.classList.contains('ocupado') || celda.classList.contains('descanso') || celda.classList.contains('ocupado-temp')) {
//       return;
//     }
    
//     // Si no tiene estado, asignarle "disponible"
//     if (!celda.classList.contains('disponible')) {
//       celda.classList.add('disponible');
//     }
//   });
  
//   // Configurar el manejo del modal y reservas
//   configurarModal();
// });

// // Función para configurar el modal y eventos de reserva
// function configurarModal() {
//   const modal = document.getElementById('modal-cita');
//   const cerrarModal = document.getElementById('cerrar-modal');
//   const btnCancelar = document.getElementById('btn-cancelar');
//   const btnReservar = document.getElementById('btn-reservar');
//   const btnReservarTemp = document.getElementById('btn-reservar-temp');
//   const diaSpan = document.getElementById('dia-cita');
//   const horaSpan = document.getElementById('hora-cita');
//   const fechaCitaInput = document.getElementById('fecha-cita');
//   const horaCitaInput = document.getElementById('hora-cita-input');
//   const contadorContainer = document.getElementById('contador-container');
//   const contadorSpan = document.getElementById('contador');
  
//   let celdaActual = null;
//   let temporizadores = {};
  
//   // Agregar evento click a todas las celdas disponibles
//   const celdasDisponibles = document.querySelectorAll('.calendario-cell.disponible');
//   celdasDisponibles.forEach(celda => {
//     celda.addEventListener('click', function() {
//       if (this.classList.contains('disponible')) {
//         celdaActual = this;
//         const dia = this.getAttribute('data-dia');
//         const hora = this.getAttribute('data-hora');
        
//         // Mostrar día y hora en el modal
//         diaSpan.textContent = dia.charAt(0).toUpperCase() + dia.slice(1);
//         horaSpan.textContent = hora;
        
//         // Asignar valores a los campos ocultos
//         fechaCitaInput.value = obtenerFecha(dia);
//         horaCitaInput.value = hora;
        
//         // Mostrar el modal
//         modal.style.display = 'block';
        
//         // Ocultar el contador si estaba visible
//         contadorContainer.style.display = 'none';
//       }
//     });
//   });
  
//   // Cerrar el modal
//   cerrarModal.addEventListener('click', function() {
//     modal.style.display = 'none';
//   });
  
//   btnCancelar.addEventListener('click', function(e) {
//     e.preventDefault();
//     modal.style.display = 'none';
//   });
  
//   // Reservar permanentemente
//   btnReservar.addEventListener('click', function(e) {
//     if (!validarFormulario()) {
//       e.preventDefault();
//       return;
//     }
    
//     if (celdaActual) {
//       // Eliminar cualquier temporizador existente para esta celda
//       const celdaId = `${celdaActual.getAttribute('data-dia')}-${celdaActual.getAttribute('data-hora')}`;
//       if (temporizadores[celdaId]) {
//         clearInterval(temporizadores[celdaId]);
//         delete temporizadores[celdaId];
//       }
      
//       // Cambiar estado a ocupado
//       celdaActual.classList.remove('disponible', 'ocupado-temp');
//       celdaActual.classList.add('ocupado');
      
//       // Guardar datos del formulario (aquí podrías enviarlos al servidor)
//       guardarDatosCita(celdaActual, 'ocupado');
      
//       // El formulario se enviará normalmente
//     }
//   });
  
//   // Reservar temporalmente (5 minutos)
//   btnReservarTemp.addEventListener('click', function(e) {
//     e.preventDefault(); // Prevenir el envío del formulario
    
//     if (!validarFormulario()) {
//       return;
//     }
    
//     if (celdaActual) {
//       // Cambiar estado a ocupado temporalmente
//       celdaActual.classList.remove('disponible', 'ocupado');
//       celdaActual.classList.add('ocupado-temp');
      
//       // Guardar datos del formulario
//       guardarDatosCita(celdaActual, 'ocupado-temp');
      
//       // Iniciar contador de 5 minutos
//       const celdaId = `${celdaActual.getAttribute('data-dia')}-${celdaActual.getAttribute('data-hora')}`;
//       let tiempoRestante = 5 * 60; // 5 minutos en segundos
      
//       // Mostrar el contador
//       contadorContainer.style.display = 'block';
//       actualizarContador(tiempoRestante);
      
//       // Crear temporizador
//       temporizadores[celdaId] = setInterval(function() {
//         tiempoRestante--;
//         actualizarContador(tiempoRestante);
        
//         if (tiempoRestante <= 0) {
//           // Tiempo agotado, liberar la celda
//           clearInterval(temporizadores[celdaId]);
//           delete temporizadores[celdaId];
          
//           celdaActual.classList.remove('ocupado-temp');
//           celdaActual.classList.add('disponible');
          
//           // Cerrar el modal si sigue abierto
//           modal.style.display = 'none';
//         }
//       }, 1000);
//     }
//   });
// }

// // Función para guardar los datos de la cita
// function guardarDatosCita(celda, estado) {
//   const tipoDocumento = document.getElementById('tipo-documento').value;
//   const numeroDocumento = document.getElementById('numero-documento').value;
//   const telefono = document.getElementById('telefono').value;
//   const direccion = document.getElementById('direccion').value;
//   const fechaNacimiento = document.getElementById('fecha-nacimiento').value;
//   const examen = document.getElementById('examen').value;
//   const fechaCita = document.getElementById('fecha-cita').value;
//   const horaCita = document.getElementById('hora-cita-input').value;
  
//   // Guardar datos en atributos data- de la celda
//   celda.setAttribute('data-tipo-documento', tipoDocumento);
//   celda.setAttribute('data-numero-documento', numeroDocumento);
//   celda.setAttribute('data-telefono', telefono);
//   celda.setAttribute('data-direccion', direccion);
//   celda.setAttribute('data-fecha-nacimiento', fechaNacimiento);
//   celda.setAttribute('data-examen', examen);
//   celda.setAttribute('data-estado', estado);
//   celda.setAttribute('data-fecha-cita', fechaCita);
  
//   // Registrar en consola para depuración
//   console.log('Cita reservada:', {
//     dia: celda.getAttribute('data-dia'),
//     hora: horaCita,
//     fecha: fechaCita,
//     tipoDocumento,
//     numeroDocumento,
//     telefono,
//     direccion,
//     fechaNacimiento,
//     examen,
//     estado
//   });
// }