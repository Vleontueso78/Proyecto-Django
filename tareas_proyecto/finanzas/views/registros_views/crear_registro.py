from django.views.generic import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ...models import RegistroFinanciero, ConfigFinanciera
from ...forms import RegistroFinancieroForm


class RegistroCreateView(LoginRequiredMixin, CreateView):
    model = RegistroFinanciero
    form_class = RegistroFinancieroForm
    template_name = "finanzas/crear_registro.html"
    success_url = reverse_lazy("finanzas:registros")

    def get_initial(self):
        """
        Carga los valores iniciales del registro
        desde la configuración financiera del usuario.
        """
        initial = super().get_initial()

        config, _ = ConfigFinanciera.objects.get_or_create(
            user=self.request.user
        )

        # Fuente única de defaults
        initial.update(
            config.get_defaults_registro()
        )

        return initial

    def form_valid(self, form):
        """
        Asigna el usuario y delega TODA la lógica
        financiera al modelo (clean + save).
        """
        form.instance.user = self.request.user
        return super().form_valid(form)