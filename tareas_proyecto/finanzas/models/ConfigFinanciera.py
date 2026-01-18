from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

from finanzas.validators import validar_presupuesto_diario
from .normalizar_decimal import normalizar_decimal

class ConfigFinanciera(models.Model):
    """
    Configuración financiera por usuario.
    Se crea automáticamente al crear el usuario.
    """

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="config_financiera",
    )

    presupuesto_diario = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[validar_presupuesto_diario],
    )

    # --------------------------------------------------
    # VALORES DEFAULT PARA REGISTROS
    # --------------------------------------------------
    default_alimento = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    default_alimento_fijo = models.BooleanField(default=False)

    default_productos = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    default_productos_fijo = models.BooleanField(default=False)

    default_ahorro_y_deuda = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    default_ahorro_y_deuda_fijo = models.BooleanField(default=False)

    default_sobrante = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    default_sobrante_fijo = models.BooleanField(default=False)

    # Fecha desde la cual se consideran registros y pendientes
    fecha_inicio_registros = models.DateField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Config financiera de {self.user.username}"

    # ======================================================
    # DEFAULTS CENTRALIZADOS PARA REGISTRO FINANCIERO
    # ======================================================
    def get_defaults_registro(self):
        """
        Devuelve un diccionario listo para:
        RegistroFinanciero.objects.create(**defaults)

        ⚠️ El sobrante NO se calcula acá.
        El modelo RegistroFinanciero decide si se respeta
        o se recalcula según 'completado'.
        """
        return {
            "para_gastar_dia": normalizar_decimal(
                self.presupuesto_diario, Decimal("0.00")
            ),

            "alimento": normalizar_decimal(
                self.default_alimento, Decimal("0.00")
            ),
            "alimento_fijo": self.default_alimento_fijo,

            "productos": normalizar_decimal(
                self.default_productos, Decimal("0.00")
            ),
            "productos_fijo": self.default_productos_fijo,

            "ahorro_y_deuda": normalizar_decimal(
                self.default_ahorro_y_deuda, Decimal("0.00")
            ),
            "ahorro_y_deuda_fijo": self.default_ahorro_y_deuda_fijo,

            "sobrante_monetario": normalizar_decimal(
                self.default_sobrante, Decimal("0.00")
            ),
            "sobrante_fijo": self.default_sobrante_fijo,
        }

    # ======================================================
    # SAVE — BLINDAJE TOTAL
    # ======================================================
    def save(self, *args, **kwargs):
        # --- Normalización total ---
        self.presupuesto_diario = normalizar_decimal(
            self.presupuesto_diario or 0
        )

        self.default_alimento = normalizar_decimal(
            self.default_alimento or 0
        )
        self.default_productos = normalizar_decimal(
            self.default_productos or 0
        )
        self.default_ahorro_y_deuda = normalizar_decimal(
            self.default_ahorro_y_deuda or 0
        )
        self.default_sobrante = normalizar_decimal(
            self.default_sobrante or 0
        )

        super().save(*args, **kwargs)