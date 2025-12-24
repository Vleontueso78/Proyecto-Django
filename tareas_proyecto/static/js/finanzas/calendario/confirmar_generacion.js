document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-calendario");
    const inputFecha = document.getElementById("fecha_inicio");
    const submitBtn = form?.querySelector("button[type='submit']");

    if (!form || !inputFecha || !submitBtn) return;

    const fechaOriginal = inputFecha.dataset.original || "";

    // ------------------------------
    // Habilitar / deshabilitar botón
    // ------------------------------
    function actualizarEstadoBoton() {
        const fechaActual = inputFecha.value;

        if (!fechaActual || fechaActual === fechaOriginal) {
            submitBtn.disabled = true;
            submitBtn.classList.add("disabled");
        } else {
            submitBtn.disabled = false;
            submitBtn.classList.remove("disabled");
        }
    }

    // Estado inicial
    actualizarEstadoBoton();

    // Al cambiar la fecha
    inputFecha.addEventListener("change", actualizarEstadoBoton);

    // ------------------------------
    // Confirmación al enviar
    // ------------------------------
    form.addEventListener("submit", (e) => {
        if (submitBtn.disabled) {
            e.preventDefault();
            return;
        }

        const fechaStr = inputFecha.value;
        if (!fechaStr) return;

        const fechaInicio = new Date(fechaStr);
        const hoy = new Date();

        fechaInicio.setHours(0, 0, 0, 0);
        hoy.setHours(0, 0, 0, 0);

        const diffMs = hoy - fechaInicio;
        const dias = Math.floor(diffMs / (1000 * 60 * 60 * 24)) + 1;

        const mensaje =
            `Se generarán registros diarios:\n\n` +
            `• Desde: ${fechaStr}\n` +
            `• Hasta: ${hoy.toISOString().slice(0, 10)}\n` +
            `• Total aproximado: ${dias} días\n\n` +
            `¿Querés continuar?`;

        if (!confirm(mensaje)) {
            e.preventDefault();
            return;
        }

        submitBtn.disabled = true;
        submitBtn.textContent = "Generando...";
    });
});