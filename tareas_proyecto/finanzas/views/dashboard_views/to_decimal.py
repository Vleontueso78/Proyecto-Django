from decimal import Decimal, InvalidOperation


def to_decimal(value, default=Decimal("0.00")):
    """
    Conversión ULTRA segura a Decimal.

    ✔ Acepta:
      - None, "", False  → default
      - "1200"
      - "1200.50"
      - "1200,50"
      - int / float / Decimal

    ✔ Nunca lanza excepción
    ✔ Nunca devuelve NaN / infinito
    ✔ Nunca devuelve negativos
    """

    if value in (None, "", False, "-", "--"):
        return default

    try:
        dec = Decimal(str(value).replace(",", "."))

        # Evitar NaN / Infinity (causan InvalidOperation en SQLite)
        if not dec.is_finite():
            return default

        # Evitar negativos
        if dec < 0:
            return default

        return dec

    except (InvalidOperation, ValueError, TypeError):
        return default