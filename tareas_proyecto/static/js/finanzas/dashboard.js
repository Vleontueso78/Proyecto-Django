// -------------------------------------------
// VALIDACIÓN DE MONTOS
// -------------------------------------------
function validarMonto(valor) {
    if (!valor) return false;

    const numero = parseFloat(valor.replace(",", "."));
    if (isNaN(numero)) {
        alert("⚠️ Agregar un monto válido.");
        return false;
    }
    return true;
}

// -------------------------------------------
// SISTEMA GLOBAL DE INPUT + LÁPIZ
// -------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const editButtons = document.querySelectorAll(".edit-btn");

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const inputId = btn.dataset.target;
            const input = document.getElementById(inputId);
            if (!input) return;

            // Activar edición
            input.removeAttribute("readonly");
            input.classList.add("editando");
            input.focus();
            input.select();

            // Handler de blur (debe ser único)
            const blurHandler = () => {

                let valor = input.value.trim();

                // Validación
                if (!validarMonto(valor)) {
                    valor = "0";
                    input.value = "0";
                }

                // -------------------------------------------
                // 🔥 Convertir a número entero al mostrar
                // -------------------------------------------
                let numero = parseFloat(valor.replace(",", "."));
                input.value = Math.round(numero).toString();
                valor = input.value;
                

                // -------------------------------------------
                // Enviar si es presupuesto diario
                // -------------------------------------------
                if (inputId === "presupuesto-diario") {
                    const hidden = document.getElementById("hidden-presupuesto");
                    const form = document.getElementById("form-presupuesto");

                    if (hidden && form) {
                        hidden.value = valor;
                        form.submit();
                    }
                }

                // Restaurar modo lectura
                input.setAttribute("readonly", true);
                input.classList.remove("editando");

                // Eliminar handler para evitar duplicados
                input.removeEventListener("blur", blurHandler);
            };

            // Agregar evento una sola vez por edición
            input.addEventListener("blur", blurHandler);
        });
    });

});