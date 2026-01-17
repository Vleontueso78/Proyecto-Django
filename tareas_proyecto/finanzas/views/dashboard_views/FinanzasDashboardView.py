from datetime import date
from decimal import Decimal

from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages

from finanzas.models import (
    RegistroFinanciero,
    ConfigFinanciera,
    normalizar_decimal,
)

from finanzas.views.registros_views.dias_pendientes import (
    obtener_dias_pendientes,
)

from .dec_int import dec_int


class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finanzas/dashboard.html"

    # =====================================================
    # POST
    # =====================================================
    def post(self, request, *args, **kwargs):

        config, _ = ConfigFinanciera.objects.get_or_create(
            user=request.user
        )

        # -------------------------------------------------
        # 1️⃣ Presupuesto diario
        # -------------------------------------------------
        if "presupuesto_diario" in request.POST:
            valor = normalizar_decimal(
                request.POST.get("presupuesto_diario"),
                default=config.presupuesto_diario,
            )

            if valor <= 0:
                messages.error(
                    request,
                    "El presupuesto debe ser mayor a cero."
                )
                return redirect("finanzas:dashboard")

            config.presupuesto_diario = valor
            config.save()

            messages.success(
                request,
                "Presupuesto actualizado correctamente."
            )
            return redirect("finanzas:dashboard")

        # Registro del día actual
        registro = RegistroFinanciero.objects.filter(
            user=request.user,
            fecha=date.today()
        ).first()

        existe_registro = registro is not None

        # -------------------------------------------------
        # 2️⃣ Fijar / desfijar valores
        # -------------------------------------------------
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")

            if not existe_registro:
                registro = RegistroFinanciero.objects.create(
                    user=request.user,
                    fecha=date.today(),
                    para_gastar_dia=config.presupuesto_diario,
                )

            if tipo == "sobrante":
                valor = normalizar_decimal(registro.sobrante_monetario)
                campo_valor = "sobrante_monetario"
                campo_fijo = "sobrante_fijo"
            else:
                valor = normalizar_decimal(request.POST.get(tipo))
                if valor <= 0:
                    messages.warning(
                        request,
                        "Debe ingresar un monto válido."
                    )
                    return redirect("finanzas:dashboard")

                campo_valor = tipo
                campo_fijo = f"{tipo}_fijo"

            setattr(
                registro,
                campo_fijo,
                not getattr(registro, campo_fijo)
            )
            setattr(registro, campo_valor, valor)
            registro.save()

            messages.success(
                request,
                f"{tipo.capitalize()} actualizado."
            )
            return redirect("finanzas:dashboard")

        # -------------------------------------------------
        # 3️⃣ Guardar día completo
        # -------------------------------------------------
        if "guardar_todo" in request.POST:
            registro, _ = RegistroFinanciero.objects.get_or_create(
                user=request.user,
                fecha=date.today(),
                defaults={
                    "para_gastar_dia": config.presupuesto_diario
                }
            )

            registro.para_gastar_dia = normalizar_decimal(
                request.POST.get("para_gastar_dia"),
                default=config.presupuesto_diario
            )
            registro.alimento = normalizar_decimal(
                request.POST.get("alimento")
            )
            registro.productos = normalizar_decimal(
                request.POST.get("productos")
            )
            registro.ahorro_y_deuda = normalizar_decimal(
                request.POST.get("ahorro_y_deuda")
            )

            registro.completado = True
            registro.save()

            messages.success(
                request,
                "Registro guardado exitosamente."
            )
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    # =====================================================
    # GET
    # =====================================================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config, _ = ConfigFinanciera.objects.get_or_create(
            user=self.request.user
        )

        presupuesto = dec_int(
            normalizar_decimal(config.presupuesto_diario)
        )

        context["presupuesto_diario"] = presupuesto
        context["presupuesto_mostrar"] = presupuesto

        # -------------------------------------------------
        # ✅ DÍAS PENDIENTES (fuente única)
        # -------------------------------------------------
        pendientes, mensaje = obtener_dias_pendientes(
            self.request.user
        )

        context["dias_pendientes"] = pendientes
        context["mensaje_pendientes"] = mensaje
        context["cantidad_pendientes"] = len(pendientes)

        # -------------------------------------------------
        # Registro del día actual
        # -------------------------------------------------
        registro = RegistroFinanciero.objects.filter(
            user=self.request.user,
            fecha=date.today()
        ).first()

        context.update({
            "registro": registro,
            "existe_registro": bool(registro),
            "dia_completado": registro.completado if registro else False,
            "valor_alimento": (
                dec_int(registro.alimento) if registro else "0"
            ),
            "valor_productos": (
                dec_int(registro.productos) if registro else "0"
            ),
            "valor_ahorro_y_deuda": (
                dec_int(registro.ahorro_y_deuda) if registro else "0"
            ),
            "valor_sobrante": (
                dec_int(registro.sobrante_monetario)
                if registro else presupuesto
            ),
            "hoy": date.today(),
        })

        # -------------------------------------------------
        # Totales
        # -------------------------------------------------
        registros = RegistroFinanciero.objects.filter(
            user=self.request.user
        )

        registros_completados = registros.filter(
            completado=True,
            para_gastar_dia__gt=0
        )

        context["total_gastado"] = sum(
            (normalizar_decimal(r.gasto_total) for r in registros),
            Decimal("0")
        )

        context["total_sobrante"] = sum(
            (
                normalizar_decimal(r.sobrante_monetario)
                for r in registros_completados
            ),
            Decimal("0")
        )

        return context