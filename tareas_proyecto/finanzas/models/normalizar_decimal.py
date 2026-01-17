from decimal import Decimal, InvalidOperation


def normalizar_decimal(valor, default=Decimal("0.00")):
    """
    Convierte cualquier valor a Decimal seguro.
    Nunca lanza excepción.

    Protege contra:
    - None
    - strings vacíos
    - valores inválidos
    - NaN / Infinity
    - números negativos
    """
    try:
        if valor in (None, "", " ", "-", "--"):
            return default

        dec = Decimal(str(valor).replace(",", "."))

        # Evitar NaN / Infinity
        if not dec.is_finite():
            return default

        # Evitar negativos
        if dec < 0:
            return default

        return dec

    except (InvalidOperation, TypeError, ValueError):
        return default