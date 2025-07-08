document.addEventListener("DOMContentLoaded", () => {
    const fechaInput = document.getElementById("fechaSeleccionada");
    const slotsContainer = document.getElementById("slotsContainer");

    fechaInput.addEventListener("change", cargarSlots);

    function cargarSlots() {
        const fecha = fechaInput.value;
        if (!fecha) return;
        
        fetch(`/consultar_calendario?fecha=${fecha}`)
            .then(response => response.json())
            .then(data => mostrarSlots(data.slots))
            .catch(error => console.error("Error al cargar slots:", error));
    }

    function mostrarSlots(slots) {
        slotsContainer.innerHTML = "";
        
        const horas = [...new Set(slots.map(slot => slot.hora))].sort();
        const diasSemana = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado"];
        
        horas.forEach(hora => {
            const fila = document.createElement("tr");
            const celdaHora = document.createElement("td");
            celdaHora.textContent = hora;
            fila.appendChild(celdaHora);
            
            diasSemana.forEach(dia => {
                const celda = document.createElement("td");
                const slot = slots.find(s => s.hora === hora && new Date(s.fecha).getDay() === diasSemana.indexOf(dia) + 1);
                
                if (slot) {
                    celda.classList.add("slot", slot.estado);
                    celda.textContent = slot.estado.charAt(0).toUpperCase() + slot.estado.slice(1);
                    if (slot.estado === "disponible") {
                        celda.addEventListener("click", () => asignarCita(slot.id));
                    }
                }
                fila.appendChild(celda);
            });
            
            slotsContainer.appendChild(fila);
        });
    }

    function asignarCita(slotId) {
        fetch("/asignar_cita", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ slot_id: slotId })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.mensaje || data.error);
            cargarSlots();
        })
        .catch(error => console.error("Error al asignar cita:", error));
    }
});
