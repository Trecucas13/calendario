// Función para manejar la liberación automática de slots temporales
document.addEventListener('DOMContentLoaded', function() {
    // Objeto para almacenar los temporizadores de cada slot
    const slotTimers = {};
    
    // Función para liberar un slot después de 5 minutos
    function releaseTemporarySlot(slot) {
        // Eliminar la clase de ocupado temporal
        slot.classList.remove('ocupado-temp');
        // Agregar la clase de disponible
        slot.classList.add('disponible');
        
        // Limpiar los atributos de datos
        slot.removeAttribute('data-paciente');
        slot.removeAttribute('data-documento');
        slot.removeAttribute('data-telefono');
        slot.removeAttribute('data-email');
        slot.removeAttribute('data-observaciones');
        slot.removeAttribute('data-estado');
        
        // Eliminar eventos de click y hover específicos
        const newSlot = slot.cloneNode(true);
        slot.parentNode.replaceChild(newSlot, slot);
        
        // Actualizar contadores
        updateCounters();
        
        // Mostrar notificación
        showNotification('Una cita temporal ha sido liberada automáticamente');
    }
    
    // Función para mostrar notificación
    function showNotification(message) {
        // Crear elemento de notificación
        const notification = document.createElement('div');
        notification.className = 'notification';
        notification.textContent = message;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Mostrar con animación
        setTimeout(() => {
            notification.classList.add('show');
        }, 10);
        
        // Ocultar después de 3 segundos
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                document.body.removeChild(notification);
            }, 300);
        }, 3000);
    }
    
    // Función para actualizar contadores
    function updateCounters() {
        const slotsDisponibles = document.querySelectorAll('.slot.disponible').length;
        document.getElementById('slotsDisponibles').textContent = slotsDisponibles;
        
        const citasReservadas = document.querySelectorAll('.slot.ocupado, .slot.ocupado-temp').length;
        document.getElementById('citasReservadas').textContent = citasReservadas;
    }
    
    // Función para configurar el temporizador para un slot temporal
    function setupTemporarySlotTimer(slot) {
        // Identificador único para el slot
        const slotId = `${slot.getAttribute('data-hora')}-${slot.getAttribute('data-dia')}`;
        
        // Cancelar temporizador existente si hay uno
        if (slotTimers[slotId]) {
            clearTimeout(slotTimers[slotId]);
        }
        
        // Agregar indicador visual de tiempo restante
        let timerIndicator = slot.querySelector('.timer-indicator');
        if (!timerIndicator) {
            timerIndicator = document.createElement('div');
            timerIndicator.className = 'timer-indicator';
            slot.appendChild(timerIndicator);
        }
        
        // Configurar nuevo temporizador (5 minutos = 300000 ms)
        slotTimers[slotId] = setTimeout(() => {
            releaseTemporarySlot(slot);
            delete slotTimers[slotId];
        }, 300000); // 5 minutos
    }
    
    // Configurar temporizadores para slots temporales existentes
    document.querySelectorAll('.slot.ocupado-temp').forEach(setupTemporarySlotTimer);
    
    // Observar cambios en el DOM para detectar nuevos slots temporales
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.type === 'attributes' && 
                mutation.attributeName === 'class' && 
                mutation.target.classList.contains('slot')) {
                
                const slot = mutation.target;
                
                // Si el slot se marca como ocupado temporalmente
                if (slot.classList.contains('ocupado-temp')) {
                    setupTemporarySlotTimer(slot);
                }
            }
        });
    });
    
    // Configurar el observador para monitorear todos los slots
    const slotsContainer = document.getElementById('slotsContainer');
    if (slotsContainer) {
        observer.observe(slotsContainer, { 
            attributes: true, 
            subtree: true, 
            attributeFilter: ['class'] 
        });
    }
    
    // Modificar el comportamiento del formulario de reserva
    const reservaForm = document.getElementById('reservaCitaForm');
    if (reservaForm) {
        const originalSubmitHandler = reservaForm.onsubmit;
        
        reservaForm.addEventListener('submit', function(event) {
            const estadoCita = document.getElementById('estadoCita').value;
            
            // Si es ocupado temporalmente, no necesitamos hacer nada especial aquí
            // El MutationObserver detectará el cambio de clase y configurará el temporizador
        });
    }
});