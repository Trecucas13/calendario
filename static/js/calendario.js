// Script para generar el calendario basado en los parámetros
document.addEventListener('DOMContentLoaded', function() {
    // Aquí se implementaría la lógica para generar el calendario
    // basado en los parámetros recibidos del formulario
    
    // Ejemplo de generación de slots de tiempo para un día
    const calendarioContenido = document.getElementById('calendario-contenido');
    
    // Función para generar un día de calendario
    function generarDiaCalendario(fecha, horaInicio, horaFin, intervalo, descansoInicio, descansoFin) {
      const dia = document.createElement('div');
      dia.className = 'dia-calendario';
      
      const fechaHeader = document.createElement('div');
      fechaHeader.className = 'fecha-header';
      fechaHeader.textContent = fecha;
      dia.appendChild(fechaHeader);
      
      // Convertir horas a minutos para facilitar cálculos
      const inicioMin = convertirHoraAMinutos(horaInicio);
      const finMin = convertirHoraAMinutos(horaFin);
      const descansoInicioMin = descansoInicio ? convertirHoraAMinutos(descansoInicio) : null;
      const descansoFinMin = descansoFin ? convertirHoraAMinutos(descansoFin) : null;
      
      // Generar slots de tiempo
      for (let tiempo = inicioMin; tiempo < finMin; tiempo += intervalo) {
        const slot = document.createElement('div');
        slot.className = 'hora-slot';
        
        // Verificar si es hora de descanso
        if (descansoInicioMin && descansoFinMin && 
            tiempo >= descansoInicioMin && tiempo < descansoFinMin) {
          slot.className += ' descanso';
          slot.innerHTML = `
            <div class="hora-label">${convertirMinutosAHora(tiempo)}</div>
            <div class="paciente-info">Descanso</div>
          `;
        } else {
          slot.className += ' disponible';
          slot.innerHTML = `
            <div class="hora-label">${convertirMinutosAHora(tiempo)}</div>
            <div class="paciente-info">Disponible</div>
          `;
        }
        
        dia.appendChild(slot);
      }
      
      return dia;
    }
    
    // Función para convertir hora (HH:MM) a minutos
    function convertirHoraAMinutos(hora) {
      const [horas, minutos] = hora.split(':').map(Number);
      return horas * 60 + minutos;
    }
    
    // Función para convertir minutos a formato hora (HH:MM)
    function convertirMinutosAHora(minutos) {
      const horas = Math.floor(minutos / 60);
      const mins = minutos % 60;
      return `${horas.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }
    
    // Ejemplo: generar 5 días de calendario
    const fechas = ['Lunes 20/07', 'Martes 21/07', 'Miércoles 22/07', 'Jueves 23/07', 'Viernes 24/07'];
    fechas.forEach(fecha => {
      const dia = generarDiaCalendario(
        fecha, 
        '08:00', 
        '17:00', 
        15, // intervalo de 15 minutos
        '12:00', 
        '13:00'
      );
      calendarioContenido.appendChild(dia);
    });
  });