from abc import ABC, abstractmethod
from decimal import Decimal


# --- Strategy Pattern ---

class IndicadorStrategy(ABC):
    """Estrategia abstracta para calcular indicadores financieros."""

    @abstractmethod
    def calcular(self, registros):
        pass


class SobranteTotalStrategy(IndicadorStrategy):
    """Calcula el sobrante total acumulado."""

    def calcular(self, registros):
        return sum((r.sobrante_monetario or Decimal(0)) for r in registros)


class TADStrategy(IndicadorStrategy):
    """Calcula el Total de Ahorro y Deuda."""

    def calcular(self, registros):
        return sum((r.ahorro_y_deuda or Decimal(0)) for r in registros)


class FactoryIndicadores:
    """Factory para devolver la estrategia según el tipo de cálculo."""

    _estrategias = {
        "sobrante": SobranteTotalStrategy(),
        "tad": TADStrategy(),
    }

    @classmethod
    def get_strategy(cls, tipo: str) -> IndicadorStrategy:
        estrategia = cls._estrategias.get(tipo)
        if not estrategia:
            raise ValueError(f"Estrategia '{tipo}' no encontrada.")
        return estrategia