from django.db import models
from django.contrib.auth.models import User

from finanzas.validators import (
    validar_monto_objetivo,
    validar_monto_actual,
)

from .normalizar_decimal import normalizar_decimal


class ObjetivoFinanciero(models.Model):
    """
    Objetivos financieros del usuario.
    Ej: comprar algo, ahorrar X monto, pagar deuda.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)

    monto_objetivo = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[validar_monto_objetivo],
    )

    monto_actual = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        validators=[validar_monto_actual],
    )

    completado = models.BooleanField(default=False)
    fecha_creacion = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Objetivo Financiero"
        verbose_name_plural = "Objetivos Financieros"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.nombre} - ${self.monto_actual} / ${self.monto_objetivo}"

    # ======================================================
    #   PROPIEDADES SEGURAS
    # ======================================================
    @property
    def progreso(self):
        monto_objetivo = normalizar_decimal(self.monto_objetivo)
        monto_actual = normalizar_decimal(self.monto_actual)

        if monto_objetivo == 0:
            return 0

        return round((monto_actual / monto_objetivo) * 100, 2)

    # ======================================================
    #   ACTUALIZACIÓN DE ESTADO
    # ======================================================
    def actualizar_estado(self):
        self.monto_actual = normalizar_decimal(self.monto_actual)
        self.monto_objetivo = normalizar_decimal(self.monto_objetivo)

        if self.monto_actual >= self.monto_objetivo:
            self.completado = True

        self.save()

    # ======================================================
    #   SAVE — BLINDAJE TOTAL
    # ======================================================
    def save(self, *args, **kwargs):
        self.monto_actual = normalizar_decimal(self.monto_actual)
        self.monto_objetivo = normalizar_decimal(self.monto_objetivo)

        super().save(*args, **kwargs)