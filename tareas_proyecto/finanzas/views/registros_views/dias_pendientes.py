from datetime import date, timedelta
from ...models import RegistroFinanciero, ConfigFinanciera


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


def obtener_dias_pendientes(usuario):
    """
    Devuelve una lista de días SIN registro entre la fecha de inicio configurada
    y el día actual.

    Un día NO se considera pendiente si existe un RegistroFinanciero,
    aunque esté incompleto.
    """
    hoy = date.today()

    # Obtener configuración financiera
    try:
        config = ConfigFinanciera.objects.get(user=usuario)
    except ConfigFinanciera.DoesNotExist:
        return [], "⚠ Todavía no configuraste una fecha de inicio en el calendario."

    fecha_inicio = config.fecha_inicio_registros

    if not fecha_inicio:
        return [], "⚠ Debes seleccionar desde qué día quieres registrar gastos."

    # Crear rango de fechas desde inicio → hoy
    rango_completo = generar_rango_fechas(fecha_inicio, hoy)

    # Fechas con al menos un registro (completo o no)
    fechas_existentes = set(
        RegistroFinanciero.objects.filter(
            user=usuario,
            fecha__gte=fecha_inicio,
            fecha__lte=hoy
        ).values_list("fecha", flat=True)
    )

    # Días faltantes = días del rango que NO tienen registro
    pendientes = [dia for dia in rango_completo if dia not in fechas_existentes]

    # Seguridad defensiva
    pendientes = [d for d in pendientes if d]

    mensaje = ""
    if not pendientes:
        mensaje = "✔ No hay días pendientes. Todo está completo."

    return pendientes, mensaje