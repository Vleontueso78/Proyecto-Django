from decimal import Decimal
from finanzas.models import normalizar_decimal


def calcular_sobrante(presupuesto, alimento, ahorro, productos):
    """
    Cálculo centralizado del sobrante monetario.

    ⚠️ REGLAS:
    - Si el presupuesto es 0 o negativo → sobrante = 0
    - Nunca devuelve valores negativos
    - Todos los valores se normalizan
    """

    # -----------------------------
    # Blindaje defensivo total
    # -----------------------------
    presupuesto = normalizar_decimal(presupuesto)
    alimento = normalizar_decimal(alimento)
    ahorro = normalizar_decimal(ahorro)
    productos = normalizar_decimal(productos)

    # -----------------------------
    # Sin presupuesto → sin sobrante
    # -----------------------------
    if presupuesto <= Decimal("0.00"):
        return Decimal("0.00")

    sobrante = presupuesto - alimento - ahorro - productos

    # -----------------------------
    # Nunca permitir negativo
    # -----------------------------
    if sobrante < Decimal("0.00"):
        sobrante = Decimal("0.00")

    return normalizar_decimal(sobrante)