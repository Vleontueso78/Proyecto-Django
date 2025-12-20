from datetime import date, timedelta
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from finanzas.models import RegistroFinanciero, ConfigFinanciera


@login_required
def lista_dias(request):
    config = ConfigFinanciera.objects.filter(user=request.user).first()

    if not config or not config.fecha_inicio_registros:
        return render(
            request,
            "finanzas/dias.html",
            {"dias": []}
        )

    hoy = date.today()
    fecha_inicio = config.fecha_inicio_registros

    dias = []
    fecha_actual = fecha_inicio

    while fecha_actual <= hoy:
        registro = RegistroFinanciero.objects.filter(
            user=request.user,
            fecha=fecha_actual
        ).first()

        dias.append({
            "fecha": fecha_actual,
            "registro": registro,
            "accion": (
                "editar"
                if registro and registro.completado
                else "completar"
            )
        })

        fecha_actual += timedelta(days=1)

    dias.reverse()

    return render(
        request,
        "finanzas/dias.html",
        {
            "dias": dias
        }
    )
