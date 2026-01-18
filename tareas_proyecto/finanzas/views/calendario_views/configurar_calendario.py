from datetime import date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ...models import ConfigFinanciera, RegistroFinanciero


@login_required
def configurar_calendario(request):
    """
    Vista exclusiva para configurar la fecha de inicio del calendario.
    Solo se permite una única vez por usuario.
    """

    # 🔎 Solo leer configuración (no crear acá)
    config = ConfigFinanciera.objects.filter(
        user=request.user
    ).first()

    if not config:
        messages.error(
            request,
            "Error de configuración del usuario."
        )
        return redirect("finanzas:dashboard")

    # 🔒 Si ya está configurado → bloqueo total
    if config.fecha_inicio_registros:
        messages.info(
            request,
            "El calendario ya fue configurado."
        )
        return redirect("finanzas:calendario_ver")

    # 🔒 Bloquear solo si existen registros creados previamente
    if RegistroFinanciero.objects.filter(
        user=request.user
    ).exists():
        messages.error(
            request,
            "No puedes configurar el calendario porque ya existen registros financieros."
        )
        return redirect("finanzas:dashboard")

    # -------------------------------------------------
    # POST
    # -------------------------------------------------
    if request.method == "POST":
        fecha_inicio_str = request.POST.get("fecha_inicio")

        if not fecha_inicio_str:
            messages.error(
                request,
                "Debes seleccionar una fecha válida."
            )
            return redirect("finanzas:configurar_calendario")

        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
        except ValueError:
            messages.error(
                request,
                "Formato de fecha inválido."
            )
            return redirect("finanzas:configurar_calendario")

        hoy = date.today()

        if fecha_inicio > hoy:
            messages.error(
                request,
                "La fecha de inicio no puede ser posterior a hoy."
            )
            return redirect("finanzas:configurar_calendario")

        if fecha_inicio.year < 2000:
            messages.error(
                request,
                "La fecha de inicio no puede ser anterior al año 2000."
            )
            return redirect("finanzas:configurar_calendario")

        # ✅ Guardado definitivo
        config.fecha_inicio_registros = fecha_inicio
        config.save()

        messages.success(
            request,
            "📅 Calendario inicial configurado correctamente."
        )

        return redirect("finanzas:calendario_ver")

    # -------------------------------------------------
    # GET
    # -------------------------------------------------
    return render(
        request,
        "finanzas/configurar_calendario.html",
        {
            "config": config,
        },
    )