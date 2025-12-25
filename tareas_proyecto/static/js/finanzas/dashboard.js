// ------------------------------------------------------
// SISTEMA GLOBAL DE INPUT + LÁPIZ (editable)
// FUNCIONA PARA:
// - Presupuesto del dashboard
// - Campos inline del detalle del día
// ------------------------------------------------------

document.addEventListener("DOMContentLoaded", () => {

    // ==================================================
    // 1. PRESUPUESTO DASHBOARD (CASO ESPECIAL)
    // ==================================================

    const editBtn = document.getElementById("btn-editar-presupuesto");
    const input = document.getElementById("presupuesto-diario");
    const wrapper = document.querySelector(".presupuesto-display");
    const hiddenInput = document.getElementById("hidden-presupuesto");
    const form = document.getElementById("form-presupuesto");
    const valorSpan = document.querySelector(".presupuesto-valor");

    if (editBtn && input && wrapper && hiddenInput && form && valorSpan) {

        let editando = false;

        // Ajusta el ancho del input según los dígitos
        function ajustarAncho() {
            const length = input.value.length || 1;
            input.style.setProperty("--digits", length);
        }

        // Inicial
        ajustarAncho();

        // ✏ ENTRAR EN EDICIÓN
        editBtn.addEventListener("click", () => {
            if (editando) return;
            editando = true;

            valorSpan.style.display = "none";
            input.hidden = false;

            input.removeAttribute("readonly");
            ajustarAncho();

            input.focus();
            input.select();

            wrapper.classList.add("editing");
            editBtn.classList.add("active");
        });

        // ⌨ TECLADO + resize en vivo
        input.addEventListener("input", ajustarAncho);

        input.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                guardarPresupuesto();
            }

            if (e.key === "Escape") {
                e.preventDefault();
                cancelarEdicion();
            }
        });

        // 💾 GUARDAR AL SALIR
        input.addEventListener("blur", () => {
            if (!editando) return;
            guardarPresupuesto();
        });

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
            ajustarAncho();
            salirEdicion();
        }

        function salirEdicion() {
            editando = false;

            input.setAttribute("readonly", true);
            input.hidden = true;

            valorSpan.style.display = "inline";

            wrapper.classList.remove("editing");
            editBtn.classList.remove("active");
        }
    }

    // ==================================================
    // 2. INLINE EDITABLES GENERALES (DETALLE DÍA)
    // ==================================================

    document.querySelectorAll(".editable-field").forEach(container => {

        const btn = container.querySelector(".edit-btn");
        const input = container.querySelector(".editable-number");
        const form = container.closest("form");

        if (!btn || !input || !form) return;

        let valorOriginal = input.value;
        let editando = false;

        // ✏ ENTRAR EN EDICIÓN
        btn.addEventListener("click", () => {
            if (editando) return;

            editando = true;
            valorOriginal = input.value;

            input.removeAttribute("readonly");
            input.focus();
            input.select();

            container.classList.add("editing");
            btn.classList.add("active");
        });

        // ⌨ TECLADO
        input.addEventListener("keydown", (e) => {

            if (e.key === "Enter") {
                e.preventDefault();
                guardar();
            }

            if (e.key === "Escape") {
                e.preventDefault();
                cancelar();
            }
        });

        // 💾 GUARDAR AL SALIR
        input.addEventListener("blur", () => {
            if (!editando) return;
            guardar();
        });

        function guardar() {
            const valor = input.value.trim();

            if (!valor) {
                cancelar();
                return;
            }

            salirEdicion();
            form.submit();
        }

        function cancelar() {
            input.value = valorOriginal;
            salirEdicion();
        }

        function salirEdicion() {
            editando = false;

            input.setAttribute("readonly", true);
            container.classList.remove("editing");
            btn.classList.remove("active");
        }
    });

});


// ------------------------------------------------------
// ANIMACIÓN ✔ AL FIJAR CAMPOS (REUTILIZABLE)
// ------------------------------------------------------

function animarCampoFijado(input) {
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