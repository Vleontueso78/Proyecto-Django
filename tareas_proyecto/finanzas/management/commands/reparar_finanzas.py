from django.core.management.base import BaseCommand
from finanzas.utils.reparador import reparar_registros_financieros
from finanzas.utils.diagnostico import diagnosticar_registros
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Ejecuta diagnóstico y reparación automática de registros financieros."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reparar",
            action="store_true",
            help="Ejecuta la reparación automática además del diagnóstico.",
        )
        parser.add_argument(
            "--verbose",
            action="store_true",
            help="Muestra información detallada.",
        )

    def handle(self, *args, **options):
        verbose = options["verbose"]
        ejecutar_reparacion = options["reparar"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Diagnóstico de Finanzas ===\n"))

        usuarios = User.objects.all()
        total_registros_global = 0

        for usuario in usuarios:
            if verbose:
                self.stdout.write(f"\nAnalizando usuario: {usuario.username}")

            resultado = diagnosticar_registros(usuario)

            total_registros_global += resultado["total_registros"]

            self.stdout.write(
                f"- {usuario.username}: {resultado['total_registros']} registros, "
                f"{resultado['errores_detectados']} errores detectados"
            )

        self.stdout.write(self.style.MIGRATE_LABEL("\n=== Fin del Diagnóstico ==="))

        if not ejecutar_reparacion:
            self.stdout.write(
                self.style.WARNING(
                    "\n>>> No se ejecutó reparación. Agrega --reparar para reparar.\n"
                )
            )
            return

        # ---------------------------------------------------
        # EJECUTAR REPARACIONES
        # ---------------------------------------------------
        self.stdout.write(self.style.SQL_TABLE("\n=== Reparación de Registros ===\n"))

        resumen_reparaciones = reparar_registros_financieros(verbose=verbose)

        self.stdout.write(self.style.SUCCESS("\n=== Reparaciones Completadas ===\n"))
        for clave, valor in resumen_reparaciones.items():
            self.stdout.write(f"{clave}: {valor}")

        self.stdout.write(self.style.SUCCESS("\n>>> Proceso finalizado con éxito.\n"))