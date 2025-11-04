from django import forms
from .models import RegistroFinanciero, ObjetivoFinanciero


class RegistroFinancieroForm(forms.ModelForm):
    """Formulario para crear o editar registros financieros."""

    class Meta:
        model = RegistroFinanciero
        fields = [
            "fecha", "para_gastar_dia", "alimento", "productos",
            "ahorro_y_deuda", "sobrante_monetario", "comentario"
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "para_gastar_dia": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "alimento": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "productos": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "ahorro_y_deuda": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "sobrante_monetario": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "comentario": forms.Textarea(attrs={"rows": 2, "class": "form-control"}),
        }


class ObjetivoFinancieroForm(forms.ModelForm):
    """Formulario para crear o editar objetivos financieros."""

    class Meta:
        model = ObjetivoFinanciero
        fields = ["nombre", "monto_objetivo", "monto_actual"]
        widgets = {
            "nombre": forms.TextInput(attrs={"class": "form-control"}),
            "monto_objetivo": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "monto_actual": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }
