from decimal import Decimal
from django.utils.timezone import now
from finanzas.models import RegistroFinanciero


def diagnosticar_registros(usuario=None):
    """
    Diagnóstico de registros financieros.
    Retorna cantidad total de registros y errores detectados.
    """

    registros = (
        RegistroFinanciero.objects.filter(user=usuario)
        if usuario
        else RegistroFinanciero.objects.all()
    )

    hoy = now().date()
    errores = 0

    campos_monetarios = [
        "alimento",
        "productos",
        "ahorro_y_deuda",
        "para_gastar_dia",
        "sobrante_monetario",
    ]

    for reg in registros:

        # 1) Fecha inválida
        if reg.fecha > hoy or reg.fecha.year < 2000:
            errores += 1

        # 2) Campos monetarios
        for campo in campos_monetarios:
            valor = getattr(reg, campo, None)

            if valor is None:
                continue

            if isinstance(valor, Decimal):
                if not valor.is_finite():
                    errores += 1
                    continue

                if valor < 0:
                    errores += 1

                if valor.quantize(Decimal("0.01")) != valor:
                    errores += 1

        # 3) Sobrante negativo
        if (
            isinstance(reg.sobrante_monetario, Decimal)
            and reg.sobrante_monetario < 0
        ):
            errores += 1

    return {
        "total_registros": registros.count(),
        "errores_detectados": errores,
    }