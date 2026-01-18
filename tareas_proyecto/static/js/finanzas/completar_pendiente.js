// ======================================================
// VALIDACIÓN DE MONTOS
// ======================================================
function validarMonto(valor) {
    if (valor === null || valor === undefined) return false;

    valor = valor.toString().trim();
    if (valor === "") return false;

    const numero = parseFloat(valor.replace(",", "."));

    if (isNaN(numero) || numero < 0) {
        alert("⚠️ Ingresá un monto válido.");
        return false;
    }
    return true;
}

// ======================================================
// CSRF
// ======================================================
function getCSRFToken() {
    return document.querySelector("[name=csrfmiddlewaretoken]")?.value;
}

// ======================================================
// EDITAR CAMPOS ✏
// ======================================================
function activarEdicion(btn) {
    const inputId = btn.dataset.target;
    const input = document.getElementById(inputId);

    if (!input) return;

    // 🚫 No permitir editar si está fijo
    if (input.hasAttribute("readonly") && input.classList.contains("input-locked")) {
        alert("🔒 Este valor está fijado y no puede editarse.");
        return;
    }

    input.removeAttribute("readonly");
    input.focus();
    input.select();
}

// ======================================================
// SISTEMA FIJAR / DESFIJAR CAMPOS 🔒
// ======================================================
async function toggleFijar(btn) {
    const inputId = btn.dataset.target;
    const input = document.getElementById(inputId);

    if (!input) return;

    const campo = input.getAttribute("name");
    if (!campo) return;

    const estabaFijo = input.hasAttribute("readonly");
    const fijar = !estabaFijo;

    // 🚫 No permitir fijar valores inválidos
    if (fijar && !validarMonto(input.value)) {
        return;
    }

    try {
        const response = await fetch(
            "/finanzas/api/fijar-default/",
            {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                    "Content-Type": "application/x-www-form-urlencoded",
                },
                body: new URLSearchParams({
                    campo: campo,
                    valor: input.value,
                    fijo: fijar.toString(),
                }),
            }
        );

        const data = await response.json();

        if (!data.ok) {
            throw new Error(data.error || "Error backend");
        }

    } catch (error) {
        console.error(error);
        alert("❌ Error al actualizar el valor fijo");
        return;
    }

    // ==================================================
    // 🎨 ACTUALIZAR UI (solo si backend OK)
    // ==================================================
    if (fijar) {
        input.setAttribute("readonly", true);
        input.classList.add("input-locked");

        btn.textContent = "🔒";
        btn.title = "Valor fijado (se propagará a otros días)";
    } else {
        input.removeAttribute("readonly");
        input.classList.remove("input-locked");

        btn.textContent = "🔓";
        btn.title = "Click para fijar este valor";

        input.focus();
        input.select();
    }
}

// ======================================================
// INIT
// ======================================================
document.addEventListener("DOMContentLoaded", () => {

    // ✏ BOTONES EDITAR
    document.querySelectorAll(".edit-btn").forEach(btn => {
        btn.addEventListener("click", () => activarEdicion(btn));
    });

    // 🔒 BOTONES FIJAR
    document.querySelectorAll(".lock-btn").forEach(btn => {
        btn.addEventListener("click", () => toggleFijar(btn));
    });

});