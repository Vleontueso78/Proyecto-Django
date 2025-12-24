from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import ConfigFinanciera


@login_required
def configurar_calendario(request):
    """
    Vista exclusiva para configurar la fecha de inicio del calendario.
    """

    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

    # 🔒 Si ya está configurado → NO mostrar más este formulario
    if config.fecha_inicio_registros:
        return redirect("finanzas:calendario_ver")

    if request.method == "POST":
        fecha_inicio_str = request.POST.get("fecha_inicio")

        if not fecha_inicio_str:
            messages.error(request, "Debes seleccionar una fecha válida.")
            return redirect("finanzas:configurar_calendario")

        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect("finanzas:configurar_calendario")

        hoy = date.today()

        if fecha_inicio > hoy:
            messages.error(request, "La fecha de inicio no puede ser superior a hoy.")
            return redirect("finanzas:configurar_calendario")

        config.fecha_inicio_registros = fecha_inicio
        config.save()

        messages.success(request, "Calendario inicial configurado correctamente.")
        return redirect("finanzas:calendario_ver")

    return render(
        request,
        "finanzas/configurar_calendario.html",
        {"config": config},
    )