from django.urls import path

from .views.dashboard_views import FinanzasDashboardView
from .views.registros_views import (
    RegistroListView,
    RegistroCreateView,
    editar_registro,
)
from .views.objetivos_views import (
    ObjetivoListView,
    ObjetivoCreateView,
)

app_name = "finanzas"

urlpatterns = [
    path("", FinanzasDashboardView.as_view(), name="dashboard"),

    # Registros
    path("registros/", RegistroListView.as_view(), name="registros"),
    path("registros/nuevo/", RegistroCreateView.as_view(), name="crear_registro"),
    path("registros/editar/<int:pk>/", editar_registro, name="editar_registro"),

    # Objetivos
    path("objetivos/", ObjetivoListView.as_view(), name="objetivos"),
    path("objetivos/nuevo/", ObjetivoCreateView.as_view(), name="crear_objetivo"),
]