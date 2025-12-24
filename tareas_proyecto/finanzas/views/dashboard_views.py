from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation

from ..models import RegistroFinanciero, ConfigFinanciera
from ..calculo_sobrante.calculadora import calcular_sobrante
from ..views.registros_views.dias_pendientes import obtener_dias_pendientes


# =====================================================
# Conversión segura a Decimal (POST)
# =====================================================
def to_decimal(value, default=Decimal("0")):
    """
    Convierte un valor a Decimal de forma segura.
    Permite valores como:
    - "1200"
    - "1200.50"
    - "1200,50"
    """
    if value in (None, "", False):
        return default
    try:
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, ValueError, TypeError):
        return default


# =====================================================
# Conversión segura para mostrar ENTEROS en templates
# =====================================================
def dec_int(value, default="0"):
    """
    Convierte Decimal → int → str sin romper.
    Ideal para mostrar números en el dashboard.
    """
    try:
        return str(int(Decimal(value)))
    except (InvalidOperation, ValueError, TypeError):
        return default


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
        # 1️⃣ Actualizar presupuesto diario
        # -------------------------------------------------
        nuevo_presupuesto = request.POST.get("presupuesto_diario")

        if nuevo_presupuesto is not None:
            valor = to_decimal(
                nuevo_presupuesto,
                config.presupuesto_diario
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

        # -------------------------------------------------
        # Obtener o crear registro de HOY
        # -------------------------------------------------
        try:
            registro = RegistroFinanciero.objects.get(
                user=request.user,
                fecha=date.today()
            )
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        # -------------------------------------------------
        # 2️⃣ Fijar / Desfijar valores
        # -------------------------------------------------
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")

            if not existe_registro:
                registro = RegistroFinanciero.objects.create(
                    user=request.user,
                    fecha=date.today(),
                    para_gastar_dia=config.presupuesto_diario,
                    alimento=Decimal("0"),
                    productos=Decimal("0"),
                    ahorro_y_deuda=Decimal("0"),
                )
                existe_registro = True

            if tipo == "sobrante":
                valor = registro.sobrante_monetario
                campo_valor = "sobrante_monetario"
                campo_fijo = "sobrante_fijo"
            else:
                valor = to_decimal(request.POST.get(tipo))
                if valor <= 0:
                    messages.warning(
                        request,
                        "Debe ingresar un monto válido."
                    )
                    return redirect("finanzas:dashboard")

                campo_valor = tipo
                campo_fijo = f"{tipo}_fijo"

            setattr(registro, campo_fijo, not getattr(registro, campo_fijo))
            setattr(registro, campo_valor, valor)

            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos,
                )

            registro.save()
            messages.success(
                request,
                f"{tipo.capitalize()} actualizado."
            )
            return redirect("finanzas:dashboard")

        # -------------------------------------------------
        # 3️⃣ Guardar todo el día
        # -------------------------------------------------
        if "guardar_todo" in request.POST:

            p = to_decimal(
                request.POST.get("para_gastar_dia"),
                config.presupuesto_diario
            )
            a = to_decimal(request.POST.get("alimento"))
            pr = to_decimal(request.POST.get("productos"))
            ad = to_decimal(request.POST.get("ahorro_y_deuda"))

            if not existe_registro:
                registro = RegistroFinanciero.objects.create(
                    user=request.user,
                    fecha=date.today(),
                    para_gastar_dia=p,
                    alimento=a,
                    productos=pr,
                    ahorro_y_deuda=ad,
                )
            else:
                registro.para_gastar_dia = p
                registro.alimento = a
                registro.productos = pr
                registro.ahorro_y_deuda = ad

            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    p, a, ad, pr
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
    # GET — CONTEXTO
    # =====================================================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config, _ = ConfigFinanciera.objects.get_or_create(
            user=self.request.user
        )

        # -----------------------------
        # Presupuesto
        # -----------------------------
        presupuesto_val = dec_int(config.presupuesto_diario)

        context["presupuesto_diario"] = presupuesto_val
        context["presupuesto_mostrar"] = presupuesto_val

        # -----------------------------
        # Días pendientes (nuevo)
        # -----------------------------
        fecha_inicio = config.fecha_inicio_registros or date.today()

        dias_pendientes = RegistroFinanciero.objects.filter(
            user=self.request.user,
            completado=False,
            fecha__gte=fecha_inicio
        ).order_by("fecha")

        context["dias_pendientes"] = dias_pendientes
        context["hay_dias_pendientes"] = dias_pendientes.exists()

        # -----------------------------
        # Sistema previo
        # -----------------------------
        pendientes, mensaje_pendientes = obtener_dias_pendientes(
            self.request.user
        )

        pendientes_limpios = sorted([d for d in pendientes if d])

        context["pendientes"] = pendientes_limpios
        context["hay_pendientes"] = bool(pendientes_limpios)
        context["mensaje_pendientes"] = mensaje_pendientes

        # -----------------------------
        # Registro de hoy
        # -----------------------------
        try:
            registro = RegistroFinanciero.objects.get(
                user=self.request.user,
                fecha=date.today()
            )
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        if existe_registro:

            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos,
                )
                registro.save()

            context["valor_alimento"] = dec_int(registro.alimento)
            context["valor_productos"] = dec_int(registro.productos)
            context["valor_ahorro_y_deuda"] = dec_int(registro.ahorro_y_deuda)
            context["valor_sobrante"] = dec_int(
                registro.sobrante_monetario
            )

        else:
            context["valor_alimento"] = "0"
            context["valor_productos"] = "0"
            context["valor_ahorro_y_deuda"] = "0"
            context["valor_sobrante"] = presupuesto_val

        registros = RegistroFinanciero.objects.filter(
            user=self.request.user
        ).order_by("-fecha")

        context.update({
            "config": config,
            "registro": registro,
            "existe_registro": existe_registro,
            "dia_completado": registro.completado if registro else False,
            "registros": registros,
            "total_gastado": sum(
                (r.gasto_total for r in registros),
                Decimal("0")
            ),
            "total_sobrante": sum(
                (r.sobrante_monetario for r in registros),
                Decimal("0")
            ),
            "hoy": date.today(),
        })

        return context