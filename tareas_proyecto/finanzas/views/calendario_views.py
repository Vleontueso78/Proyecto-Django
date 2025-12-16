# Configuracion del calendario

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta

from ..models import RegistroFinanciero, ConfigFinanciera


@login_required
def configurar_calendario(request):

    # Obtener o crear configuración del usuario
    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

    if request.method == "POST":
        fecha_inicio_str = request.POST.get("fecha_inicio")

        # Validación básica
        if not fecha_inicio_str:
            messages.error(request, "Debes seleccionar una fecha válida.")
            return redirect("finanzas:configurar_calendario")

        try:
            fecha_inicio = date.fromisoformat(fecha_inicio_str)
        except ValueError:
            messages.error(request, "Formato de fecha inválido.")
            return redirect("finanzas:configurar_calendario")

        hoy = date.today()

        # Evitar fechas futuras
        if fecha_inicio > hoy:
            messages.error(request, "La fecha de inicio no puede ser superior a hoy.")
            return redirect("finanzas:configurar_calendario")

        # Guardar configuración
        config.fecha_inicio_registros = fecha_inicio
        config.save()

        # Crear todos los días que falten
        actual = fecha_inicio
        while actual <= hoy:
            RegistroFinanciero.objects.get_or_create(
                user=request.user,
                fecha=actual,
                defaults={
                    "para_gastar_dia": 0,
                    "alimento": 0,
                    "productos": 0,
                    "ahorro_y_deuda": 0,
                    "sobrante_monetario": 0,
                    "alimento_fijo": False,
                    "productos_fijo": False,
                    "ahorro_y_deuda_fijo": False,
                    "sobrante_fijo": False,
                    "completado": False,
                },
            )
            actual += timedelta(days=1)

        messages.success(request, "Fecha de inicio configurada correctamente.")
        return redirect("finanzas:dashboard")

    return render(request, "finanzas/configurar_calendario.html", {
        "config": config,
    })