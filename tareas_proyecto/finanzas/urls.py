from django.urls import path
from .views.calendario_views import configurar_calendario

from .views.dashboard_views import FinanzasDashboardView
from .views.registros_views import (
    RegistroListView,
    RegistroCreateView,
    editar_registro,
    registros_pendientes,
    completar_pendiente_por_fecha,
)
from .views.objetivos_views import (
    ObjetivoListView,
    ObjetivoCreateView,
)

app_name = "finanzas"

urlpatterns = [
    path("", FinanzasDashboardView.as_view(), name="dashboard"),

    # ======================
    #     REGISTROS
    # ======================

    path("registros/", RegistroListView.as_view(), name="registros"),
    path("registros/nuevo/", RegistroCreateView.as_view(), name="crear_registro"),
    path("registros/editar/<int:pk>/", editar_registro, name="editar_registro"),

    # DÍAS PENDIENTES — NUEVO MODO POR FECHA
    path("registros/pendientes/", registros_pendientes, name="registros_pendientes"),
    path("registros/pendiente/<str:fecha_str>/", completar_pendiente_por_fecha, name="completar_pendiente_por_fecha"),

    # ======================
    #     OBJETIVOS
    # ======================

    path("objetivos/", ObjetivoListView.as_view(), name="objetivos"),
    path("objetivos/nuevo/", ObjetivoCreateView.as_view(), name="crear_objetivo"),
    
    path("calendario/", configurar_calendario, name="configurar_calendario"),
]