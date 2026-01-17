from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from finanzas.models import RegistroFinanciero, ConfigFinanciera


class RegistroListView(LoginRequiredMixin, ListView):
    model = RegistroFinanciero
    template_name = "finanzas/registros/registros.html"
    context_object_name = "registros"
    paginate_by = 30

    def get_queryset(self):
        # Obtener configuración del usuario
        config, _ = ConfigFinanciera.objects.get_or_create(
            user=self.request.user
        )

        fecha_inicio = config.fecha_inicio_registros

        queryset = RegistroFinanciero.objects.filter(
            user=self.request.user,
            completado=True
        )

        # Respetar fecha de inicio del calendario si existe
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)

        return queryset.order_by("-fecha")