// -------------------------------------------
// VALIDACIÓN DE MONTOS
// -------------------------------------------
function validarMonto(valor) {
    if (valor === "" || isNaN(parseFloat(valor))) {
        alert("⚠️ Agregar monto válido.");
        return false;
    }
    return true;
}

// -------------------------------------------
// SISTEMA GLOBAL DE INPUT + LÁPIZ
// -------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    // Buscar todos los botones de edición
    const editButtons = document.querySelectorAll(".edit-btn");

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            // Obtener el ID del input objetivo
            const inputId = btn.dataset.target;
            const input = document.getElementById(inputId);

            if (!input) return;

            // Habilitar edición
            input.removeAttribute("readonly");
            input.classList.add("editando");

            // Focus + selección
            input.focus();
            input.select();

            // Cuando el usuario salga del input → guardar
            input.addEventListener("blur", () => {

                const valor = input.value.trim();

                if (!validarMonto(valor)) {
                    input.value = "0";
                }

                // Enviar al backend si es presupuesto
                if (inputId === "presupuesto-input") {
                    const hidden = document.getElementById("hidden-presupuesto");
                    const form = document.getElementById("form-presupuesto");

                    if (hidden && form) {
                        hidden.value = valor;
                        form.submit();
                    }
                }

                // Volver readonly
                input.setAttribute("readonly", true);
                input.classList.remove("editando");

            }, { once: true });
        });
    });

});