document.addEventListener("DOMContentLoaded", function() {
    const desc = document.getElementById("id_descripcion");
    if (desc && desc.value.trim() === "Sin descripción") {
        desc.value = "";
    }
});