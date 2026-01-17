from decimal import Decimal, InvalidOperation
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# ============================================================
#   UTILIDADES BASE
# ============================================================

def safe_decimal(value, default=Decimal("0.00")):
    """
    Convierte cualquier valor a Decimal seguro.
    Nunca lanza excepción.
    """
    try:
        if value in [None, "", " ", "-", "--"]:
            return default
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        return default

# ============================================================
#   VALIDADORES GENÉRICOS
# ============================================================

def validar_decimal_no_negativo(value):
    """
    Valida que un valor decimal no sea negativo
    y sea convertible a Decimal.
    """
    valor = safe_decimal(value)

    if valor < 0:
        raise ValidationError(
            _("El valor no puede ser negativo."),
            code="valor_negativo"
        )


def validar_decimal_positivo_o_cero(value):
    """
    Alias semántico del validador no negativo.
    """
    validar_decimal_no_negativo(value)


def validar_decimal_mayor_a_cero(value):
    """
    Valida que el valor sea estrictamente mayor a cero.
    """
    valor = safe_decimal(value)

    if valor <= 0:
        raise ValidationError(
            _("El valor debe ser mayor a cero."),
            code="valor_no_positivo"
        )


# ============================================================
#   VALIDADORES DE NEGOCIO (FINANZAS)
# ============================================================

def validar_presupuesto_diario(value):
    """
    Presupuesto diario:
    - no negativo
    - razonable (no infinito / basura)
    """
    valor = safe_decimal(value)

    if valor < 0:
        raise ValidationError(
            _("El presupuesto diario no puede ser negativo."),
            code="presupuesto_negativo"
        )

    if valor > Decimal("100000000"):
        raise ValidationError(
            _("El presupuesto diario es irrealmente alto."),
            code="presupuesto_irreal"
        )


def validar_gasto_individual(value):
    """
    Validador estándar para:
    - alimento
    - productos
    - ahorro_y_deuda
    """
    valor = safe_decimal(value)

    if valor < 0:
        raise ValidationError(
            _("El gasto no puede ser negativo."),
            code="gasto_negativo"
        )


def validar_sobrante(value):
    """
    El sobrante:
    - puede ser cero
    - no puede ser negativo
    """
    valor = safe_decimal(value)

    if valor < 0:
        raise ValidationError(
            _("El sobrante no puede ser negativo."),
            code="sobrante_negativo"
        )


# ============================================================
#   VALIDADORES DE OBJETIVOS
# ============================================================

def validar_monto_objetivo(value):
    """
    Monto objetivo:
    - estrictamente mayor a cero
    """
    valor = safe_decimal(value)

    if valor <= 0:
        raise ValidationError(
            _("El monto objetivo debe ser mayor a cero."),
            code="objetivo_invalido"
        )


def validar_monto_actual(value):
    """
    Monto actual:
    - no negativo
    """
    valor = safe_decimal(value)

    if valor < 0:
        raise ValidationError(
            _("El monto actual no puede ser negativo."),
            code="monto_actual_negativo"
        )