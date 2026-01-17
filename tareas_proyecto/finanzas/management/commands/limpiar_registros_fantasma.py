from django.core.management.base import BaseCommand
from decimal import Decimal

from finanzas.models import RegistroFinanciero
from finanzas.models.normalizar_decimal import normalizar_decimal


class Command(BaseCommand):
    help = "Elimina registros financieros fantasma (sin datos reales)"

    def handle(self, *args, **options):

        fantasmas = RegistroFinanciero.objects.filter(
            completado=False,
            para_gastar_dia=Decimal("0.00"),
            alimento=Decimal("0.00"),
            productos=Decimal("0.00"),
            ahorro_y_deuda=Decimal("0.00"),
        ).exclude(
            sobrante_monetario=Decimal("0.00")
        )

        total = fantasmas.count()

        if total == 0:
            self.stdout.write(
                self.style.SUCCESS("✔ No se encontraron registros fantasma.")
            )
            return

        self.stdout.write(
            self.style.WARNING(
                f"⚠ Se encontraron {total} registros fantasma."
            )
        )

        # Mostrar detalle (opcional pero útil)
        for r in fantasmas:
            self.stdout.write(
                f" - {r.user.username} | {r.fecha} | sobrante={r.sobrante_monetario}"
            )

        confirm = input(
            "\n¿Desea ELIMINAR estos registros? (s/N): "
        ).lower()

        if confirm != "s":
            self.stdout.write(
                self.style.ERROR("❌ Operación cancelada.")
            )
            return

        fantasmas.delete()

        self.stdout.write(
            self.style.SUCCESS(
                f"🧹 {total} registros fantasma eliminados correctamente."
            )
        )