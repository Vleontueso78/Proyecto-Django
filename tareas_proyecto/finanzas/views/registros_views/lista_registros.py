from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from finanzas.models import RegistroFinanciero

class RegistroListView(LoginRequiredMixin, ListView):
    model = RegistroFinanciero
    template_name = "finanzas/registros/registros.html"
    context_object_name = "registros"
    paginate_by = 30  

    def get_queryset(self):
        # Solo registros completados
        return (
            RegistroFinanciero.objects
            .filter(user=self.request.user)
            .order_by('-fecha')
        )