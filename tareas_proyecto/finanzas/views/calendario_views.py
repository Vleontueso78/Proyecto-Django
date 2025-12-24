# Configuracion del calendario

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import date, timedelta
from calendar import monthrange
import calendar

from ..models import RegistroFinanciero, ConfigFinanciera
from ..calendario.services import asegurar_registros_hasta_hoy

MESES_ES = [
    "",  # índice 0 vacío
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"
]

@login_required
def configurar_calendario(request):
    """
    Vista exclusiva para configurar la fecha de inicio del calendario.
    Si ya existe una fecha configurada, redirige al calendario visual.
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

        # Guardar configuración
        config.fecha_inicio_registros = fecha_inicio
        config.save()

        messages.success(request, "Calendario inicial configurado correctamente.")
        return redirect("finanzas:calendario_ver")

    return render(
        request,
        "finanzas/configurar_calendario.html",
        {"config": config},
    )


@login_required
def calendario_ver(request):
    """
    Vista de calendario visual con navegación por meses.
    """

    config = ConfigFinanciera.objects.filter(user=request.user).first()

    if not config or not config.fecha_inicio_registros:
        return redirect("finanzas:configurar_calendario")

    # 🔄 Asegurar que existan todos los registros hasta hoy
    asegurar_registros_hasta_hoy(user=request.user)

    hoy = date.today()

    # Año y mes desde query params o actual
    try:
        year = int(request.GET.get("year", hoy.year))
        month = int(request.GET.get("month", hoy.month))
    except ValueError:
        year = hoy.year
        month = hoy.month

    # Normalizar mes
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1

    # 🔤 Nombre del mes (Ej: Octubre)
    nombre_mes = calendar.month_name[month].capitalize()

    # Días del mes actual
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

    # ==========================
    # Navegación por meses
    # ==========================

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

    # 🔐 Mostrar flecha ⬅ solo si el mes anterior es válido
    fecha_prev_mes = date(prev_year, prev_month, 1)
    mostrar_prev = fecha_prev_mes >= config.fecha_inicio_registros.replace(day=1)

    nombre_mes = MESES_ES[month]

    context = {
        "dias": dias,
        "mes": month,
        "anio": year,
        "nombre_mes": nombre_mes,
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

    context = {
        "registro": registro,
        "fecha": fecha,
    }

    return render(
        request,
        "finanzas/detalle_dia.html",
        context
    )