from datetime import date, timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from ...models import RegistroFinanciero, ConfigFinanciera


def generar_rango_fechas(desde, hasta):
    """Genera una lista de fechas entre dos días (incluye ambos)."""
    dias = []
    actual = desde
    while actual <= hasta:
        dias.append(actual)
        actual += timedelta(days=1)
    return dias


def obtener_dias_pendientes(usuario):
    """Devuelve todos los días que NO tienen registro desde la fecha elegida hasta hoy."""
    hoy = date.today()

    # Buscar configuración financiera
    try:
        config = ConfigFinanciera.objects.get(user=usuario)
    except ConfigFinanciera.DoesNotExist:
        return [], "⚠ Todavía no configuraste una fecha de inicio en el calendario."

    fecha_inicio = config.fecha_inicio_registros

    if not fecha_inicio:
        return [], "⚠ Debes seleccionar desde qué día quieres registrar gastos."

    # Generar rango completo
    rango_completo = generar_rango_fechas(fecha_inicio, hoy)

    # Fechas registradas
    fechas_existentes = set(
        RegistroFinanciero.objects.filter(
            user=usuario,
            fecha__range=[fecha_inicio, hoy]
        ).values_list("fecha", flat=True)
    )

    # Determinar días sin registro
    pendientes = [dia for dia in rango_completo if dia not in fechas_existentes]

    # 🔥 FILTRO CRÍTICO:
    # Elimina valores corruptos, None, vacíos o no-fechas
    pendientes = [d for d in pendientes if d]

    mensaje = ""
    if not pendientes:
        mensaje = "✔ No hay días pendientes. Todo está completo."

    return pendientes, mensaje


@login_required
def registros_pendientes(request):
    pendientes, mensaje = obtener_dias_pendientes(request.user)

    return render(
        request,
        "finanzas/registros/registros_lista.html",
        {
            "pendientes": pendientes,
            "mensaje": mensaje
        }
    )