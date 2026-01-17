from datetime import date, timedelta
from django.db import transaction

from ..models import RegistroFinanciero, ConfigFinanciera


# ============================================================
# Generar registros desde una fecha hasta hoy
# ============================================================
def generar_registros_desde_fecha(*, user, fecha_inicio):
    """
    Genera registros financieros diarios desde fecha_inicio hasta hoy.
    NO completa días, solo asegura su existencia.

    Devuelve la cantidad de registros creados.
    """
    hoy = date.today()
    creados = 0

    config = ConfigFinanciera.objects.get(user=user)

    # Defaults centralizados
    defaults_base = config.get_defaults_registro()
    defaults_base["completado"] = False

    with transaction.atomic():
        actual = fecha_inicio

        while actual <= hoy:
            _, creado = RegistroFinanciero.objects.get_or_create(
                user=user,
                fecha=actual,
                defaults=defaults_base,
            )

            if creado:
                creados += 1

            actual += timedelta(days=1)

    return creados


# ============================================================
# Asegurar registros hasta hoy (uso calendario)
# ============================================================
def asegurar_registros_hasta_hoy(*, user):
    """
    Asegura que existan registros diarios desde la fecha
    configurada hasta hoy.

    Pensada para usarse al entrar al calendario.
    """
    config = ConfigFinanciera.objects.filter(
        user=user
    ).first()

    if not config or not config.fecha_inicio_registros:
        return 0

    return generar_registros_desde_fecha(
        user=user,
        fecha_inicio=config.fecha_inicio_registros
    )