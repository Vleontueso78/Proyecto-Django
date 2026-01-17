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

    # --------------------------------------------------------
    # 1️⃣ Configuración financiera
    # --------------------------------------------------------
    config = ConfigFinanciera.objects.filter(
        user=request.user
    ).first()

    if not config or not config.fecha_inicio_registros:
        return redirect("finanzas:configurar_calendario")

    # --------------------------------------------------------
    # 2️⃣ Asegurar registros desde inicio hasta hoy
    # --------------------------------------------------------
    asegurar_registros_hasta_hoy(user=request.user)

    hoy = date.today()

    # --------------------------------------------------------
    # 3️⃣ Año y mes desde query params
    # --------------------------------------------------------
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

    # --------------------------------------------------------
    # 4️⃣ Días del mes
    # --------------------------------------------------------
    _, total_dias = monthrange(year, month)

    registros_mes = {
        r.fecha: r
        for r in RegistroFinanciero.objects.filter(
            user=request.user,
            fecha__year=year,
            fecha__month=month,
        )
    }

    dias = []
    for dia in range(1, total_dias + 1):
        fecha = date(year, month, dia)

        # ❌ No mostrar fechas fuera del rango permitido
        if fecha < config.fecha_inicio_registros or fecha > hoy:
            continue

        registro = registros_mes.get(fecha)

        dias.append({
            "fecha": fecha,
            "registro": registro,
            "completado": registro.completado if registro else False,
        })

    # --------------------------------------------------------
    # 5️⃣ Navegación de meses
    # --------------------------------------------------------
    if month == 1:
        prev_month = 12
        prev_year = year - 1
    else:
        prev_month = month - 1
        prev_year = year

    if month == 12:
        next_month = 1
        next_year = year + 1
    else:
        next_month = month + 1
        next_year = year

    # 🔐 Mostrar flecha anterior solo si no se pasa del inicio
    inicio = config.fecha_inicio_registros
    mostrar_prev = (
        prev_year > inicio.year
        or (prev_year == inicio.year and prev_month >= inicio.month)
    )

    # --------------------------------------------------------
    # 6️⃣ Contexto
    # --------------------------------------------------------
    context = {
        "dias": dias,
        "anio": year,
        "mes": month,
        "nombre_mes": date(year, month, 1).strftime("%B").capitalize(),
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