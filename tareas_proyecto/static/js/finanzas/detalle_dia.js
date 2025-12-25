document.addEventListener('DOMContentLoaded', () => {

    document.querySelectorAll('.editable-field').forEach(field => {

        const input = field.querySelector('.editable-number');
        const btn = field.querySelector('.edit-btn');
        const display = field.querySelector('.presupuesto-display') || field;

        if (!input || !btn) return;

        const initialValue = input.value;

        // ✏️ Click en editar
        btn.addEventListener('click', () => {
            input.removeAttribute('readonly');
            input.focus();

            input.classList.add('editing');
            display.classList.add('editing');
            btn.classList.add('active');

            // Opcional: ocultar botón mientras edita
            btn.style.display = 'none';
        });

        // ⌨️ Feedback mientras escribe
        input.addEventListener('input', () => {
            if (input.value !== initialValue) {
                display.classList.add('dirty');
            } else {
                display.classList.remove('dirty');
            }
        });

        // 👀 Al salir del input
        input.addEventListener('blur', () => {
            input.setAttribute('readonly', true);

            input.classList.remove('editing');
            display.classList.remove('editing');
            btn.classList.remove('active');

            // Volver a mostrar botón
            btn.style.display = 'inline-flex';
        });

    });

});