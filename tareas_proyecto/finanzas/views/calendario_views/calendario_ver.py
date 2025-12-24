from datetime import date
from calendar import monthrange

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ...models import RegistroFinanciero, ConfigFinanciera
from ...calendario.services import asegurar_registros_hasta_hoy


@login_required
def calendario_ver(request):
    """
    Vista de calendario visual con navegación por meses.
    """

    config = ConfigFinanciera.objects.filter(user=request.user).first()

    if not config or not config.fecha_inicio_registros:
        return redirect("finanzas:configurar_calendario")

    # 🔄 Asegurar registros hasta hoy
    asegurar_registros_hasta_hoy(user=request.user)

    hoy = date.today()

    # Año y mes desde query params
    try:
        year = int(request.GET.get("year", hoy.year))
        month = int(request.GET.get("month", hoy.month))
    except (TypeError, ValueError):
        year = hoy.year
        month = hoy.month

    # Normalizar mes
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # Días del mes
    _, total_dias = monthrange(year, month)

    dias = []
    for dia in range(1, total_dias + 1):
        fecha = date(year, month, dia)

        if fecha < config.fecha_inicio_registros:
            continue

        registro = RegistroFinanciero.objects.filter(
            user=request.user,
            fecha=fecha
        ).first()

        dias.append({
            "fecha": fecha,
            "registro": registro,
        })

    # Mes anterior
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    # Mes siguiente
    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # 🔐 Mostrar flecha anterior solo si corresponde
    fecha_prev_mes = date(prev_year, prev_month, 1)
    mostrar_prev = fecha_prev_mes >= config.fecha_inicio_registros.replace(day=1)

    context = {
        "dias": dias,
        "anio": year,
        "mes": month,
        "nombre_mes": hoy.replace(month=month).strftime("%B").capitalize(),
        "prev_year": prev_year,
        "prev_month": prev_month,
        "next_year": next_year,
        "next_month": next_month,
        "mostrar_prev": mostrar_prev,
        "today": hoy,
    }

    return render(
        request,
        "finanzas/calendario_ver.html",
        context
    )