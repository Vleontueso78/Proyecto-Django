from datetime import date, timedelta
from django.db import transaction

from ..models import RegistroFinanciero, ConfigFinanciera


def generar_registros_desde_fecha(*, user, fecha_inicio):
    """
    Genera registros financieros diarios desde fecha_inicio hasta hoy.
    Devuelve la cantidad de registros creados.
    """
    hoy = date.today()
    creados = 0

    config = ConfigFinanciera.objects.get(user=user)

    with transaction.atomic():
        actual = fecha_inicio
        while actual <= hoy:
            _, creado = RegistroFinanciero.objects.get_or_create(
                user=user,
                fecha=actual,
                defaults={
                    "para_gastar_dia": config.presupuesto_diario,
                    "alimento": config.default_alimento,
                    "productos": config.default_productos,
                    "ahorro_y_deuda": config.default_ahorro_y_deuda,
                    "sobrante_monetario": config.default_sobrante,
                    "alimento_fijo": config.default_alimento_fijo,
                    "productos_fijo": config.default_productos_fijo,
                    "ahorro_y_deuda_fijo": config.default_ahorro_y_deuda_fijo,
                    "sobrante_fijo": config.default_sobrante_fijo,
                    "completado": False,
                },
            )
            if creado:
                creados += 1
            actual += timedelta(days=1)

    return creados


# ✅ NUEVA FUNCIÓN – USO PARA CALENDARIO
def asegurar_registros_hasta_hoy(*, user):
    """
    Asegura que existan registros diarios desde la fecha configurada hasta hoy.
    Pensada para usarse al entrar al calendario.
    """
    config = ConfigFinanciera.objects.filter(user=user).first()

    if not config or not config.fecha_inicio_registros:
        return 0

    return generar_registros_desde_fecha(
        user=user,
        fecha_inicio=config.fecha_inicio_registros
    )