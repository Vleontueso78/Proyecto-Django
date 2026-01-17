from django import forms
from decimal import Decimal

from .models import RegistroFinanciero, ObjetivoFinanciero, ConfigFinanciera
from .models.normalizar_decimal import normalizar_decimal


# ============================================================
#   FORM BASE — UTILIDAD PARA DECIMALES SEGUROS
# ============================================================
class DecimalSeguroForm(forms.Form):
    """
    Form base para limpiar decimales de forma segura.
    Nunca lanza excepción.
    """

    def clean_decimal(self, value, default=Decimal("0.00")):
        return normalizar_decimal(value, default)


# ============================================================
#   REGISTRO FINANCIERO
# ============================================================
class RegistroFinancieroForm(forms.ModelForm, DecimalSeguroForm):
    """Formulario para crear o editar registros financieros."""

    class Meta:
        model = RegistroFinanciero
        fields = [
            "fecha",
            "para_gastar_dia",
            "alimento",
            "productos",
            "ahorro_y_deuda",
            "comentario",
        ]
        widgets = {
            "fecha": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
            "para_gastar_dia": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "alimento": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "productos": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "ahorro_y_deuda": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "comentario": forms.Textarea(
                attrs={"rows": 2, "class": "form-control"}
            ),
        }

    # ------------------------------
    # Limpieza por campo
    # ------------------------------
    def clean_para_gastar_dia(self):
        return self.clean_decimal(
            self.cleaned_data.get("para_gastar_dia")
        )

    def clean_alimento(self):
        return self.clean_decimal(
            self.cleaned_data.get("alimento")
        )

    def clean_productos(self):
        return self.clean_decimal(
            self.cleaned_data.get("productos")
        )

    def clean_ahorro_y_deuda(self):
        return self.clean_decimal(
            self.cleaned_data.get("ahorro_y_deuda")
        )

    # ------------------------------
    # Limpieza global
    # ------------------------------
    def clean(self):
        cleaned = super().clean()

        presupuesto = cleaned.get("para_gastar_dia", Decimal("0"))
        gastos = (
            cleaned.get("alimento", Decimal("0"))
            + cleaned.get("productos", Decimal("0"))
            + cleaned.get("ahorro_y_deuda", Decimal("0"))
        )

        if gastos > presupuesto:
            raise forms.ValidationError(
                "La suma de los gastos no puede superar el presupuesto diario."
            )

        return cleaned

# ============================================================
#   OBJETIVOS FINANCIEROS
# ============================================================
class ObjetivoFinancieroForm(forms.ModelForm, DecimalSeguroForm):
    """Formulario para crear o editar objetivos financieros."""

    class Meta:
        model = ObjetivoFinanciero
        fields = ["nombre", "monto_objetivo", "monto_actual"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={"class": "form-control"}
            ),
            "monto_objetivo": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "monto_actual": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
        }

    def clean_monto_objetivo(self):
        valor = self.clean_decimal(self.cleaned_data.get("monto_objetivo"))
        if valor <= 0:
            raise forms.ValidationError(
                "El monto objetivo debe ser mayor a 0."
            )
        return valor

    def clean_monto_actual(self):
        return self.clean_decimal(self.cleaned_data.get("monto_actual"))


# ============================================================
#   CONFIGURACIÓN FINANCIERA
# ============================================================
class ConfigFinancieraForm(forms.ModelForm, DecimalSeguroForm):
    """Formulario de configuración financiera del usuario."""

    class Meta:
        model = ConfigFinanciera
        fields = [
            "presupuesto_diario",
            "default_alimento",
            "default_alimento_fijo",
            "default_productos",
            "default_productos_fijo",
            "default_ahorro_y_deuda",
            "default_ahorro_y_deuda_fijo",
            "default_sobrante",
            "default_sobrante_fijo",
            "fecha_inicio_registros",
        ]
        widgets = {
            "presupuesto_diario": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "default_alimento": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "default_productos": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "default_ahorro_y_deuda": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "default_sobrante": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "fecha_inicio_registros": forms.DateInput(
                attrs={"type": "date", "class": "form-control"}
            ),
        }

    def clean_presupuesto_diario(self):
        return self.clean_decimal(self.cleaned_data.get("presupuesto_diario"))

    def clean_default_alimento(self):
        return self.clean_decimal(self.cleaned_data.get("default_alimento"))

    def clean_default_productos(self):
        return self.clean_decimal(self.cleaned_data.get("default_productos"))

    def clean_default_ahorro_y_deuda(self):
        return self.clean_decimal(
            self.cleaned_data.get("default_ahorro_y_deuda")
        )

    def clean_default_sobrante(self):
        return self.clean_decimal(self.cleaned_data.get("default_sobrante"))