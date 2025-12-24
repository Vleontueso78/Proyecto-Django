// ------------------------------------------------------
// SISTEMA GLOBAL DE INPUT + LÁPIZ (editable)
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const editBtn = document.getElementById("btn-editar-presupuesto");
    const input = document.getElementById("presupuesto-diario");
    const wrapper = document.querySelector(".presupuesto-display");
    const hiddenInput = document.getElementById("hidden-presupuesto");
    const form = document.getElementById("form-presupuesto");

    if (!editBtn || !input || !wrapper) return;

    // Crear span visual si no existe
    let valorSpan = document.querySelector(".presupuesto-valor");

    if (!valorSpan) {
        valorSpan = document.createElement("span");
        valorSpan.className = "presupuesto-valor";
        valorSpan.textContent = input.value;
        wrapper.appendChild(valorSpan);
    }

    // ✏ Entrar en modo edición
    editBtn.addEventListener("click", () => {
        wrapper.classList.add("editing");
        input.removeAttribute("readonly");
        input.focus();
        input.select();
    });

    // Guardar con Enter / cancelar con Escape
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            e.preventDefault();
            guardarPresupuesto();
        }

        if (e.key === "Escape") {
            cancelarEdicion();
        }
    });

    // Guardar al salir del input
    input.addEventListener("blur", guardarPresupuesto);

    function guardarPresupuesto() {
        const valor = input.value.trim();
        if (!valor) {
            cancelarEdicion();
            return;
        }

        valorSpan.textContent = valor;
        hiddenInput.value = valor;

        salirEdicion();
        form.submit();
    }

    function cancelarEdicion() {
        input.value = valorSpan.textContent;
        salirEdicion();
    }

    function salirEdicion() {
        wrapper.classList.remove("editing");
        input.setAttribute("readonly", true);
    }

});

// ------------------------------------------------------
// ANIMACIÓN ✔ AL FIJAR CAMPOS
// ------------------------------------------------------
function animarCampoFijado(idCampo) {
    const input = document.getElementById(idCampo);
    if (!input) return;

    input.classList.add("input-fijado");

    const check = document.createElement("span");
    check.textContent = "✔";
    check.classList.add("fijado-check");
    check.style.marginLeft = "8px";
    check.style.fontWeight = "bold";
    check.style.color = "#22c55e";

    input.parentElement.appendChild(check);

    setTimeout(() => check.remove(), 900);
    setTimeout(() => input.classList.remove("input-fijado"), 1200);
}

// Detectar inputs fijados por el backend
["input-alimento", "input-productos", "input-ahorro"].forEach(id => {
    const el = document.getElementById(id);
    if (el && el.hasAttribute("readonly")) {
        animarCampoFijado(id);
    }
});

// ------------------------------------------------------
// DESBLOQUEAR INPUTS FIJOS CON CLICK EN 🔒
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const lockButtons = document.querySelectorAll(".lock-btn");

    lockButtons.forEach(btn => {
        btn.addEventListener("click", () => {

            const inputId = btn.dataset.target;
            const input = document.getElementById(inputId);
            if (!input) return;

            if (!input.hasAttribute("data-locked")) return;

            input.removeAttribute("readonly");
            input.removeAttribute("data-locked");
            input.classList.remove("input-locked");

            btn.textContent = "🔓";
            btn.title = "Campo desbloqueado";

            input.focus();
            input.select();
        });
    });

});