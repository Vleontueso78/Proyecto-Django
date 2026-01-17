from decimal import Decimal, InvalidOperation


def dec_int(value, default="0"):
    """
    Conversión ULTRA segura para mostrar enteros en templates.

    ✔ Acepta:
      - Decimal
      - int / float
      - str numérico ("1200", "1200.50", "1200,50")
      - None

    ✔ Devuelve siempre string
    ✔ Nunca lanza excepción
    ✔ Nunca devuelve NaN / infinito
    ✔ Nunca rompe templates
    """

    if value in (None, "", False):
        return default

    try:
        dec = Decimal(str(value).replace(",", "."))

        # Evitar NaN / Infinity (rompen SQLite y templates)
        if not dec.is_finite():
            return default

        return str(int(dec))

    except (InvalidOperation, ValueError, TypeError):
        return default