// ------------------------------------------------------
// VALIDACIÓN DE MONTOS
// ------------------------------------------------------
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

// ------------------------------------------------------
// SISTEMA GLOBAL DE INPUT + LÁPIZ (editable)
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const editButtons = document.querySelectorAll(".edit-btn");

    editButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const inputId = btn.dataset.target;
            const input = document.getElementById(inputId);
            if (!input) return;

            // Habilitar edición
            input.removeAttribute("readonly");
            input.classList.add("editando");
            input.focus();
            input.select();

            // Handler único para cuando se sale del input
            const blurHandler = () => {

                let valor = input.value.trim();

                // Validación
                if (!validarMonto(valor)) {
                    valor = "0";
                    input.value = "0";
                }

                // Convertir a número real
                let numero = parseFloat(valor.replace(",", "."));

                // ----------------------------------
                // Caso especial → **presupuesto**
                // (se guarda como entero)
                // ----------------------------------
                if (inputId === "presupuesto-diario") {
                    numero = Math.round(numero);
                    input.value = numero.toString();

                    const hidden = document.getElementById("hidden-presupuesto");
                    const form = document.getElementById("form-presupuesto");

                    if (hidden && form) {
                        hidden.value = numero;
                        form.submit();
                    }

                } else {
                    // Otros inputs permiten decimales
                    input.value = numero.toFixed(2);
                }

                // Volver a modo lectura
                input.setAttribute("readonly", true);
                input.classList.remove("editando");

                // Limpieza → evitar múltiples listeners
                input.removeEventListener("blur", blurHandler);
            };

            // Registrar handler de blur UNA sola vez
            input.addEventListener("blur", blurHandler);
        });
    });

});

function animarCampoFijado(idCampo) {
    const input = document.getElementById(idCampo);
    if (!input) return;

    // 1) Agregar clase visual
    input.classList.add("input-fijado");

    // 2) Crear un ✔ junto al input
    const check = document.createElement("span");
    check.textContent = "✔";
    check.classList.add("fijado-check");
    check.style.marginLeft = "8px";
    check.style.fontWeight = "bold";
    check.style.color = "#22c55e";

    input.parentElement.appendChild(check);

    // 3) Eliminar el ✔ después de la animación
    setTimeout(() => {
        check.remove();
    }, 900);

    // 4) Remover animación para permitir otra si se vuelve a editar
    setTimeout(() => {
        input.classList.remove("input-fijado");
    }, 1200);
}

// Detectar inputs fijados por el backend
["input-alimento", "input-productos", "input-ahorro"].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.hasAttribute("readonly")) {
        animarCampoFijado(id);
    }
});