from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import RegistroFinanciero, ConfigFinanciera


@login_required
def detalle_dia(request, fecha_str):
    """
    Vista de detalle de un día específico.
    """

    config = ConfigFinanciera.objects.filter(user=request.user).first()

    if not config or not config.fecha_inicio_registros:
        return redirect("finanzas:configurar_calendario")

    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        messages.error(request, "Fecha inválida.")
        return redirect("finanzas:calendario_ver")

    if fecha < config.fecha_inicio_registros:
        messages.error(request, "Fecha fuera del rango permitido.")
        return redirect("finanzas:calendario_ver")

    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    if not registro:
        messages.error(request, "No existe registro para ese día.")
        return redirect("finanzas:calendario_ver")

    return render(
        request,
        "finanzas/detalle_dia.html",
        {
            "registro": registro,
            "fecha": fecha,
        }
    )