from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from decimal import Decimal

from finanzas.validators import (
    validar_presupuesto_diario,
    validar_gasto_individual,
    validar_sobrante,
)

from .normalizar_decimal import normalizar_decimal
from finanzas.calculo_sobrante.calculadora import calcular_sobrante


class RegistroFinanciero(models.Model):
    """
    Registro financiero diario por usuario.
    Solo puede existir UNO por usuario y fecha.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField()

    para_gastar_dia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[validar_presupuesto_diario],
        help_text="Presupuesto disponible para el día",
    )

    alimento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[validar_gasto_individual],
    )

    productos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[validar_gasto_individual],
    )

    ahorro_y_deuda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[validar_gasto_individual],
    )

    sobrante_monetario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[validar_sobrante],
    )

    # Indicadores de gastos fijos
    alimento_fijo = models.BooleanField(default=False)
    productos_fijo = models.BooleanField(default=False)
    ahorro_y_deuda_fijo = models.BooleanField(default=False)
    sobrante_fijo = models.BooleanField(default=False)

    comentario = models.TextField(blank=True, null=True)
    completado = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Registro Financiero"
        verbose_name_plural = "Registros Financieros"
        unique_together = ("user", "fecha")

    def __str__(self):
        return f"{self.fecha} - {self.user.username}"

    # ======================================================
    # PROPIEDADES CALCULADAS (NO GUARDADAS)
    # ======================================================
    @property
    def gasto_total(self):
        return (
            normalizar_decimal(self.alimento)
            + normalizar_decimal(self.productos)
            + normalizar_decimal(self.ahorro_y_deuda)
        )

    @property
    def balance_diario(self):
        return normalizar_decimal(self.para_gastar_dia) - self.gasto_total

    @property
    def sobrante_efectivo(self):
        """
        Sobrante real del día (solo válido si está completado).
        """
        if not self.completado:
            return Decimal("0.00")

        return normalizar_decimal(self.sobrante_monetario)

    # ======================================================
    # VALIDACIONES DE NEGOCIO
    # ======================================================
    def clean(self):
        """
        Validaciones cruzadas de negocio.
        Se ejecuta vía full_clean().
        """

        para_gastar = normalizar_decimal(self.para_gastar_dia)
        alimento = normalizar_decimal(self.alimento)
        productos = normalizar_decimal(self.productos)
        ahorro = normalizar_decimal(self.ahorro_y_deuda)

        gastos = alimento + productos + ahorro

        # ❌ Gastos mayores al presupuesto
        if gastos > para_gastar:
            raise ValidationError(
                "La suma de los gastos no puede superar el presupuesto diario."
            )

        # ❌ Presupuesto negativo
        if para_gastar < Decimal("0.00"):
            raise ValidationError(
                {"para_gastar_dia": "El presupuesto diario no puede ser negativo."}
            )

    # ======================================================
    # FIJAR / DESFIJAR VALORES
    # ======================================================
    def fijar_valor(self, campo: str, valor=None):
        """
        Alterna el estado fijo de un campo y opcionalmente actualiza su valor.
        """
        mapping = {
            "alimento": ("alimento", "alimento_fijo"),
            "productos": ("productos", "productos_fijo"),
            "ahorro_y_deuda": ("ahorro_y_deuda", "ahorro_y_deuda_fijo"),
            "sobrante": ("sobrante_monetario", "sobrante_fijo"),
        }

        if campo not in mapping:
            return

        campo_valor, campo_fijo = mapping[campo]

        if valor is not None:
            setattr(self, campo_valor, normalizar_decimal(valor))

        setattr(self, campo_fijo, not getattr(self, campo_fijo))
        self.save()

    # ======================================================
    # SAVE — BLINDAJE TOTAL
    # ======================================================
    def save(self, *args, **kwargs):
        # --- Normalización base ---
        self.para_gastar_dia = normalizar_decimal(self.para_gastar_dia or 0)
        self.alimento = normalizar_decimal(self.alimento or 0)
        self.productos = normalizar_decimal(self.productos or 0)
        self.ahorro_y_deuda = normalizar_decimal(self.ahorro_y_deuda or 0)

        # --- Validaciones ---
        self.full_clean()

        # ==================================================
        # 🔒 REGLA DE NEGOCIO CLAVE
        # ==================================================
        if not self.completado:
            # Un día NO completado nunca tiene sobrante
            self.sobrante_monetario = Decimal("0.00")

        else:
            # Día completado → calcular sobrante
            if self.sobrante_fijo:
                self.sobrante_monetario = normalizar_decimal(
                    self.sobrante_monetario or 0
                )
            else:
                self.sobrante_monetario = calcular_sobrante(
                    self.para_gastar_dia,
                    self.alimento,
                    self.ahorro_y_deuda,
                    self.productos,
                )

        super().save(*args, **kwargs)