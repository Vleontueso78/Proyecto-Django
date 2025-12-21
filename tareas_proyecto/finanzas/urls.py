from django.urls import path

# DASHBOARD
from .views.dashboard_views import FinanzasDashboardView

# CALENDARIO
from .views.calendario_views import configurar_calendario

# REGISTROS
from .views.registros_views.lista_registros import RegistroListView
from .views.registros_views.crear_registro import RegistroCreateView
from .views.registros_views.editar_registro import editar_registro

# PENDIENTES (flujo correcto)
from .views.registros_views.completar_pendientes import (
    completar_pendiente_por_fecha,
    registros_pendientes,
)

# DÍAS
from .dias.views import lista_dias

# OBJETIVOS
from .views.objetivos_views import ObjetivoListView, ObjetivoCreateView


app_name = "finanzas"


urlpatterns = [
    # ======================
    #     DASHBOARD
    # ======================
    path("", FinanzasDashboardView.as_view(), name="dashboard"),

    # ======================
    #     REGISTROS
    # ======================
    path("registros/", RegistroListView.as_view(), name="registros"),
    path("registros/nuevo/", RegistroCreateView.as_view(), name="crear_registro"),
    path("registros/editar/<int:pk>/", editar_registro, name="editar_registro"),

    # ======================
    #     DÍAS
    # ======================
    path("registros/dias/", lista_dias, name="registros_dias"),

    # ======================
    #     PENDIENTES
    # ======================
    path("registros/pendientes/", registros_pendientes, name="registros_pendientes"),
    path(
        "registros/pendiente/<str:fecha_str>/",
        completar_pendiente_por_fecha,
        name="completar_pendiente_por_fecha"
    ),

    # ======================
    #     OBJETIVOS
    # ======================
    path("objetivos/", ObjetivoListView.as_view(), name="objetivos"),
    path("objetivos/nuevo/", ObjetivoCreateView.as_view(), name="crear_objetivo"),

    # ======================
    #     CONFIGURACIÓN
    # ======================
    path("calendario/", configurar_calendario, name="configurar_calendario"),
]
