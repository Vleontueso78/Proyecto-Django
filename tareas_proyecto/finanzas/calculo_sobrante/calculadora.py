# calculadora.py
# El archivo 'sobrante.js' esta en: C:\Users\usuario\Desktop\practicaAlumnosNavarro\Proyecto Django\tareas_proyecto\static\js\finanzas\sobrante.js

from decimal import Decimal

def calcular_sobrante(presupuesto, alimento, ahorro):
    """
    Cálculo centralizado del sobrante.
    Se usa en el backend (views) para asegurar coherencia en la BD.
    """
    try:
        presupuesto = Decimal(presupuesto)
        alimento = Decimal(alimento)
        ahorro = Decimal(ahorro)
    except:
        return Decimal("0.00")

    sobrante = presupuesto - alimento - ahorro
    return sobrante if sobrante >= 0 else Decimal("0.00")