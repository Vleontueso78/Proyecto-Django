from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from ...models import RegistroFinanciero, ConfigFinanciera
from ...forms import RegistroFinancieroForm


@login_required
def editar_registro(request, pk):
    registro = get_object_or_404(
        RegistroFinanciero,
        pk=pk,
        user=request.user
    )

    config, _ = ConfigFinanciera.objects.get_or_create(
        user=request.user
    )

    # --------------------------------------------------
    # Defaults centralizados (solo para UI)
    # --------------------------------------------------
    defaults = config.get_defaults_registro()

    # --------------------------------------------------
    # Campos editables según flags
    # --------------------------------------------------
    campos_editables = ["para_gastar_dia"]

    if not registro.alimento_fijo:
        campos_editables.append("alimento")

    if not registro.productos_fijo:
        campos_editables.append("productos")

    if not registro.ahorro_y_deuda_fijo:
        campos_editables.append("ahorro_y_deuda")

    # --------------------------------------------------
    # POST
    # --------------------------------------------------
    if request.method == "POST":
        form = RegistroFinancieroForm(
            request.POST,
            instance=registro
        )

        # Deshabilitar campos fijos
        for campo in form.fields:
            if campo not in campos_editables:
                form.fields[campo].disabled = True

        if form.is_valid():
            # clean() + save() del modelo
            form.save()

            messages.success(
                request,
                "Registro actualizado correctamente."
            )
            return redirect("finanzas:registros")

    # --------------------------------------------------
    # GET
    # --------------------------------------------------
    else:
        form = RegistroFinancieroForm(instance=registro)

        # Aplicar defaults SOLO si el valor está vacío / cero
        for campo, valor in defaults.items():
            if campo in form.fields:
                actual = getattr(registro, campo, None)
                if not actual:
                    form.initial[campo] = valor

        # Deshabilitar campos fijos
        for campo in form.fields:
            if campo not in campos_editables:
                form.fields[campo].disabled = True

    return render(
        request,
        "finanzas/registros/registro_editar.html",
        {
            "form": form,
            "registro": registro,
            "config": config,
        }
    )