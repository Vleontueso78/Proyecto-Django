# finanzas/views/calendario_views.py

from datetime import date
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ..models import ConfigFinanciera
from ..calendario.services import generar_registros_desde_fecha


@login_required
def configurar_calendario(request):

    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

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

        # Guardar fecha solo si cambia
        if config.fecha_inicio_registros != fecha_inicio:
            config.fecha_inicio_registros = fecha_inicio
            config.save()

        creados = generar_registros_desde_fecha(
            user=request.user,
            fecha_inicio=fecha_inicio
        )

        if creados > 0:
            messages.success(
                request,
                f"Calendario configurado correctamente. Se crearon {creados} días."
            )
        else:
            messages.info(
                request,
                "El calendario ya estaba actualizado. No se crearon días nuevos."
            )

        return redirect("finanzas:dashboard")

    return render(
        request,
        "finanzas/configurar_calendario.html",
        {"config": config},
    )