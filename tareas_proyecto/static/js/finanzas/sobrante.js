function getPresupuestoActual() {
    // Toma el valor del strong mostrado en pantalla
    const texto = document.getElementById("valor-presupuesto-actual").innerText;

    // Quita símbolos ($)
    return parseFloat(texto.replace("$", "")) || 0;
}

function fixNumber(value) {
    if (!value) return 0;
    return parseFloat(value.toString().replace(",", ".")) || 0;
}

function calcularSobranteFrontend() {
    const presupuesto = getPresupuestoActual();

    const alimento = fixNumber(document.getElementById("input-alimento").value);
    const ahorro = fixNumber(document.getElementById("input-ahorro").value);

    const sobrante = presupuesto - alimento - ahorro;

    document.getElementById("input-sobrante").value = sobrante.toFixed(2);
}

document.addEventListener("DOMContentLoaded", () => {
    const campos = ["input-alimento", "input-ahorro"];

    campos.forEach(id => {
        const campo = document.getElementById(id);
        if (campo) campo.addEventListener("input", calcularSobranteFrontend);
    });

    // Calcular al cargar la página
    calcularSobranteFrontend();
});