// ------------------------------------------------------
// OBTENER PRESUPUESTO ACTUAL
// ------------------------------------------------------
function getPresupuestoActual() {
    const valor = document.getElementById("presupuesto-diario").value;
    const numero = parseFloat(valor);
    return isNaN(numero) ? 0 : numero;
}

// ------------------------------------------------------
// NORMALIZAR VALORES NUMÉRICOS
// ------------------------------------------------------
function fixNumber(value) {
    if (value === null || value === undefined) return 0;
    value = value.toString().replace(",", ".");
    const numero = parseFloat(value);
    return isNaN(numero) ? 0 : numero;
}

// ------------------------------------------------------
// CÁLCULO PRINCIPAL
// ------------------------------------------------------
function calcularSobranteFrontend() {
    const presupuesto = getPresupuestoActual();

    const alimento = fixNumber(document.getElementById("input-alimento").value);
    const productos = fixNumber(document.getElementById("input-productos").value);
    const ahorro   = fixNumber(document.getElementById("input-ahorro").value);

    const sobrante = presupuesto - alimento - productos - ahorro;

    const campoSobrante = document.getElementById("input-sobrante");
    campoSobrante.value = sobrante.toFixed(2);

    // Colores dinámicos
    campoSobrante.classList.remove("sobrante-positivo", "sobrante-negativo");

    if (sobrante < 0) {
        campoSobrante.classList.add("sobrante-negativo");
    } else {
        campoSobrante.classList.add("sobrante-positivo");
    }
}

// ------------------------------------------------------
// EVENTOS
// ------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {

    const camposDinamicos = [
        "input-alimento",
        "input-productos",
        "input-ahorro"
    ];

    camposDinamicos.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) {
            campo.addEventListener("input", calcularSobranteFrontend);
        }
    });

    // Calcular al cargar la página
    calcularSobranteFrontend();
});