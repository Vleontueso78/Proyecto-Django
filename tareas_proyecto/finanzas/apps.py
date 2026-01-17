from django.apps import AppConfig


class FinanzasConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "finanzas"

    def ready(self):
        # Registrar signals
        import finanzas.models.crear_config_usuario  # noqa