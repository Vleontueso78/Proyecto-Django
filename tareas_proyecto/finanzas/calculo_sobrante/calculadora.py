from decimal import Decimal

def calcular_sobrante(presupuesto, alimento, ahorro, productos):
    """
    Cálculo centralizado del sobrante.
    Ahora recibe los 4 valores necesarios.
    """
    try:
        presupuesto = Decimal(presupuesto)
        alimento = Decimal(alimento)
        ahorro = Decimal(ahorro)
        productos = Decimal(productos)
    except:
        return Decimal("0.00")

    sobrante = presupuesto - alimento - ahorro - productos
    return sobrante if sobrante >= 0 else Decimal("0.00")