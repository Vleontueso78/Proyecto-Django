from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..calculo_sobrante.calculadora import calcular_sobrante

from ..models import RegistroFinanciero
from ..forms import RegistroFinancieroForm

# ===========================
#   REGISTROS FINANCIEROS
# ===========================
class RegistroListView(LoginRequiredMixin, ListView):
    """Lista de registros financieros del usuario."""
    model = RegistroFinanciero
    template_name = "finanzas/registros.html"
    context_object_name = "registros"

    def get_queryset(self):
        return RegistroFinanciero.objects.filter(user=self.request.user).order_by('-fecha')


class RegistroCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo registro financiero."""
    model = RegistroFinanciero
    form_class = RegistroFinancieroForm
    template_name = "finanzas/crear_registro.html"
    success_url = reverse_lazy("finanzas:registros")

    def form_valid(self, form):
        form.instance.user = self.request.user
        
        p = form.cleaned_data.get("para_gastar_dia")
        a = form.cleaned_data.get("alimento")
        ad = form.cleaned_data.get("ahorro_y_deuda")
        pr = form.cleaned_data.get("productos")

        form.instance.sobrante_monetario = calcular_sobrante(p, a, ad, pr)
        
        return super().form_valid(form)