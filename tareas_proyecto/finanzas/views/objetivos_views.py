from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy

from ..models import ObjetivoFinanciero
from ..forms import ObjetivoFinancieroForm


# ===========================
#   OBJETIVOS FINANCIEROS
# ===========================

class ObjetivoListView(LoginRequiredMixin, ListView):
    """Lista de objetivos financieros del usuario."""
    model = ObjetivoFinanciero
    template_name = "finanzas/objetivos.html"
    context_object_name = "objetivos"
    paginate_by = 20

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(user=self.request.user)
            .order_by("-fecha_creacion", "-id")
        )


class ObjetivoCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo objetivo financiero."""
    model = ObjetivoFinanciero
    form_class = ObjetivoFinancieroForm
    template_name = "finanzas/crear_objetivo.html"
    success_url = reverse_lazy("finanzas:objetivos")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)