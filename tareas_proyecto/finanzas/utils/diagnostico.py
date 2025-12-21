from finanzas.models import RegistroFinanciero
from django.utils.timezone import now


def diagnosticar_registros(usuario=None):
    """
    Diagnóstico de registros financieros.
    Retorna cantidad total de registros y errores detectados.
    """

    if usuario:
        registros = RegistroFinanciero.objects.filter(user=usuario)
    else:
        registros = RegistroFinanciero.objects.all()

    hoy = now().date()
    errores = 0

    # Campos numéricos reales del modelo
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

        # 2) Revisar cada campo monetario
        for campo in campos_monetarios:
            valor = getattr(reg, campo, None)

            if valor is None:
                continue

            # Valores negativos
            if valor < 0:
                errores += 1

            # Más de dos decimales
            if round(valor, 2) != valor:
                errores += 1

        # 3) Sobrante negativo
        if reg.sobrante_monetario < 0:
            errores += 1

    return {
        "total_registros": registros.count(),
        "errores_detectados": errores,
    }