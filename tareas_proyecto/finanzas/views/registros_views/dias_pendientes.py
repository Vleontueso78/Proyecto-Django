from datetime import date, timedelta

from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from ...models import RegistroFinanciero, ConfigFinanciera


# ------------------------------------------------------------
# Utilidad: generar rango de fechas
# ------------------------------------------------------------
def generar_rango_fechas(desde, hasta):
    """
    Genera una lista de fechas entre dos días (inclusive).
    """
    dias = []
    actual = desde
    while actual <= hasta:
        dias.append(actual)
        actual += timedelta(days=1)
    return dias


# ------------------------------------------------------------
# Lógica central: días pendientes
# ------------------------------------------------------------
def obtener_dias_pendientes(usuario):
    """
    Devuelve una lista de fechas consideradas pendientes
    y un mensaje informativo opcional.

    Un día es pendiente si:
    - Está entre la fecha de inicio configurada y hoy
    - NO tiene ningún RegistroFinanciero COMPLETADO

    Puede existir un registro incompleto y el día
    sigue siendo pendiente.
    """

    hoy = date.today()

    config, _ = ConfigFinanciera.objects.get_or_create(
        user=usuario
    )

    fecha_inicio = config.fecha_inicio_registros

    if not fecha_inicio:
        return [], "⚠️ Debes configurar una fecha de inicio para registrar gastos."

    # --------------------------------------------------------
    # Rango completo de fechas
    # --------------------------------------------------------
    rango_fechas = generar_rango_fechas(
        fecha_inicio,
        hoy
    )

    # --------------------------------------------------------
    # Fechas que ya están COMPLETADAS
    # --------------------------------------------------------
    fechas_completadas = set(
        RegistroFinanciero.objects.filter(
            user=usuario,
            completado=True,
            fecha__gte=fecha_inicio,
            fecha__lte=hoy,
        ).values_list("fecha", flat=True)
    )

    # --------------------------------------------------------
    # Pendientes = días sin ningún registro completado
    # --------------------------------------------------------
    pendientes = [
        fecha for fecha in rango_fechas
        if fecha not in fechas_completadas
    ]

    mensaje = ""
    if not pendientes:
        mensaje = "✅ No hay días pendientes. Estás al día."

    return pendientes, mensaje


# ------------------------------------------------------------
# Vista: lista de días pendientes
# ------------------------------------------------------------
@login_required
def registros_pendientes(request):
    """
    Muestra la lista de días pendientes utilizando
    la lógica central de obtener_dias_pendientes().
    """

    pendientes, mensaje = obtener_dias_pendientes(
        request.user
    )

    return render(
        request,
        "finanzas/registros/pendientes.html",
        {
            "pendientes": sorted(pendientes),
            "mensaje": mensaje,
        }
    )