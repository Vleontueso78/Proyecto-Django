document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("form-calendario");
    const inputFecha = document.getElementById("fecha_inicio");

    if (!form || !inputFecha) return;

    form.addEventListener("submit", (e) => {
        const fecha = inputFecha.value;

        if (!fecha) return;

        const mensaje =
            `Vas a generar registros diarios desde:\n\n` +
            `${fecha}\n\n` +
            `¿Querés continuar?`;

        if (!confirm(mensaje)) {
            e.preventDefault();
        }
    });
});