from django.urls import path
from .views import (
    FinanzasDashboardView,
    RegistroListView,
    RegistroCreateView,
    ObjetivoListView,
    ObjetivoCreateView,
)

app_name = "finanzas"

urlpatterns = [
    # Página principal del panel financiero
    path('', FinanzasDashboardView.as_view(), name='dashboard'),

    # Historial de registros financieros
    path('registros/', RegistroListView.as_view(), name='registros'),

    # Crear un nuevo registro manualmente
    path('registros/nuevo/', RegistroCreateView.as_view(), name='crear_registro'),

    # Lista de objetivos financieros
    path('objetivos/', ObjetivoListView.as_view(), name='objetivos'),

    # Crear un nuevo objetivo
    path('objetivos/nuevo/', ObjetivoCreateView.as_view(), name='crear_objetivo'),
]