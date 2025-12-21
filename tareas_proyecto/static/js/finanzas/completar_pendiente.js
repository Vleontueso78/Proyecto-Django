// ======================================================
// VALIDACIÓN DE MONTOS
// ======================================================
function validarMonto(valor) {
    if (valor === null || valor === undefined) return false;

    valor = valor.toString().trim();
    if (valor === "") return false;

    const numero = parseFloat(valor.replace(",", "."));

    if (isNaN(numero)) {
        alert("⚠️ Ingresá un monto válido.");
        return false;
    }
    return true;
}

// ======================================================
// DESBLOQUEAR INPUTS FIJOS CON CANDADO 🔒
// ======================================================
document.addEventListener("DOMContentLoaded", () => {

    const lockButtons = document.querySelectorAll(".lock-btn");

    lockButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const inputId = btn.dataset.target;
            const input = document.getElementById(inputId);

            if (!input) return;

            const locked = input.hasAttribute("readonly");

            if (locked) {
                // 🔓 Desbloquear
                input.removeAttribute("readonly");
                input.classList.remove("input-locked");
                input.focus();
                input.select();

                btn.textContent = "🔓";
                btn.title = "Click para volver a bloquear";
                btn.classList.add("unlocked");
            } else {
                // 🔒 Volver a bloquear
                input.setAttribute("readonly", true);
                input.classList.add("input-locked");

                btn.textContent = "🔒";
                btn.title = "Este valor está fijado";
                btn.classList.remove("unlocked");
            }
        });
    });

});