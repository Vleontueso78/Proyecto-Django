from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from ...models import RegistroFinanciero, ConfigFinanciera
from ...calculo_sobrante.calculadora import calcular_sobrante


def editar_registro(request, pk):
    registro = get_object_or_404(RegistroFinanciero, pk=pk, user=request.user)
    config = ConfigFinanciera.objects.get(user=request.user)

    # Valores por defecto (si el usuario dejó algo vacío)
    defaults = {
        "para_gastar_dia": config.presupuesto_diario,
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    # Valores del formulario que se muestran al cargar la página
    form_values = {
        "para_gastar_dia": registro.para_gastar_dia or defaults["para_gastar_dia"],
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    if request.method == "POST":
        # Obtiene valores ingresados por el usuario o los defaults
        p = float(request.POST.get("para_gastar_dia") or defaults["para_gastar_dia"])
        a = float(request.POST.get("alimento") or defaults["alimento"])
        pr = float(request.POST.get("productos") or defaults["productos"])
        ad = float(request.POST.get("ahorro_y_deuda") or defaults["ahorro_y_deuda"])

        # Actualizar campos
        registro.para_gastar_dia = p
        registro.alimento = a
        registro.productos = pr
        registro.ahorro_y_deuda = ad

        # Recalcular sobrante solo si NO es fijo
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        registro.save()

        messages.success(request, "Registro actualizado correctamente.")
        return redirect("finanzas:registros")

    return render(request, "finanzas/registros/registro_editar.html", {
        "registro": registro,
        "config": config,
        "defaults": defaults,
        "form_values": form_values,
    })