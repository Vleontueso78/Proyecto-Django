from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.db.models.signals import post_save
from django.dispatch import receiver


class RegistroFinanciero(models.Model):
    """
    Modelo principal que registra los gastos diarios de un usuario.
    Incluye campos para gastos fijos y variables, más cálculos automáticos.
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateField(default=date.today)

    # Presupuesto diario asignado para ese día
    para_gastar_dia = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Presupuesto disponible para el día",
    )

    # Gastos principales
    alimento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    productos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ahorro_y_deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sobrante_monetario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Indicadores de gasto fijo
    alimento_fijo = models.BooleanField(default=False)
    productos_fijo = models.BooleanField(default=False)
    ahorro_y_deuda_fijo = models.BooleanField(default=False)
    sobrante_fijo = models.BooleanField(default=False)

    # Comentario opcional
    comentario = models.TextField(blank=True, null=True)

    # Indica si el día está completamente registrado
    completado = models.BooleanField(default=False)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "Registro Financiero"
        verbose_name_plural = "Registros Financieros"

    def __str__(self):
        return f"{self.fecha} - {self.user.username}"

    # ==========================
    # PROPIEDADES CALCULADAS
    # ==========================
    @property
    def gasto_total(self):
        return self.alimento + self.productos + self.ahorro_y_deuda

    @property
    def balance_diario(self):
        return self.para_gastar_dia - self.gasto_total

    @property
    def sobrante_efectivo(self):
        return self.sobrante_monetario + self.balance_diario

    # ==========================
    # MARCAR VALORES FIJOS
    # ==========================
    def fijar_valor(self, campo: str, valor=None):
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
            setattr(self, campo_valor, valor)

        actual = getattr(self, campo_fijo)
        setattr(self, campo_fijo, not actual)

        self.save()

    # ==========================
    # SAVE AUTOMÁTICO
    # ==========================
    def save(self, *args, **kwargs):
        from .calculo_sobrante.calculadora import calcular_sobrante

        if not self.sobrante_fijo:
            self.sobrante_monetario = calcular_sobrante(
                self.para_gastar_dia,
                self.alimento,
                self.ahorro_y_deuda,
                self.productos
            )

        super().save(*args, **kwargs)


class ObjetivoFinanciero(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    monto_objetivo = models.DecimalField(max_digits=12, decimal_places=2)
    monto_actual = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    completado = models.BooleanField(default=False)
    fecha_creacion = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Objetivo Financiero"
        verbose_name_plural = "Objetivos Financieros"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"{self.nombre} - ${self.monto_actual} / ${self.monto_objetivo}"

    @property
    def progreso(self):
        if self.monto_objetivo == 0:
            return 0
        return round((self.monto_actual / self.monto_objetivo) * 100, 2)

    def actualizar_estado(self):
        if self.monto_actual >= self.monto_objetivo:
            self.completado = True
            self.save()


class ConfigFinanciera(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    presupuesto_diario = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    default_alimento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_alimento_fijo = models.BooleanField(default=False)

    default_productos = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_productos_fijo = models.BooleanField(default=False)

    default_ahorro_y_deuda = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_ahorro_y_deuda_fijo = models.BooleanField(default=False)

    default_sobrante = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    default_sobrante_fijo = models.BooleanField(default=False)

    fecha_inicio_registros = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Config financiera de {self.user.username}"


# ==========================
# SIGNAL: crear config automática
# ==========================
@receiver(post_save, sender=User)
def crear_config_usuario(sender, instance, created, **kwargs):
    if created:
        ConfigFinanciera.objects.create(user=instance)