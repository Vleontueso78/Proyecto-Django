from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ...models import RegistroFinanciero, ConfigFinanciera
from ...forms import RegistroFinancieroForm
from ...calculo_sobrante.calculadora import calcular_sobrante

class RegistroCreateView(LoginRequiredMixin, CreateView):
    model = RegistroFinanciero
    form_class = RegistroFinancieroForm
    template_name = "finanzas/crear_registro.html"
    success_url = reverse_lazy("finanzas:registros")

    def get_initial(self):
        """Carga el presupuesto diario como valor inicial."""
        initial = super().get_initial()
        config = ConfigFinanciera.objects.get(user=self.request.user)
        initial["para_gastar_dia"] = config.presupuesto_diario
        return initial

    def form_valid(self, form):
        """Asigna el usuario y calcula el sobrante antes de guardar."""
        form.instance.user = self.request.user

        p = form.cleaned_data["para_gastar_dia"]
        a = form.cleaned_data["alimento"]
        pr = form.cleaned_data["productos"]
        ad = form.cleaned_data["ahorro_y_deuda"]

        # Solo calcular si NO es un sobrante fijo
        if not form.instance.sobrante_fijo:
            form.instance.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        return super().form_valid(form)