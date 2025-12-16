from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation

from ..models import RegistroFinanciero, ConfigFinanciera
from ..calculo_sobrante.calculadora import calcular_sobrante
from ..views.registros_views.dias_pendientes import obtener_dias_pendientes


# ---------------------------------------------
# Conversión segura a Decimal
# ---------------------------------------------
def to_decimal(value, default=Decimal("0")):
    """
    Convierte un valor a Decimal de forma segura.
    Permite valores como "1200", "1.200", "1,200".
    """
    if not value:
        return default
    try:
        return Decimal(str(value).replace(",", "."))
    except:
        return default


class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finanzas/dashboard.html"

    # =====================================================
    # POST
    # =====================================================
    def post(self, request, *args, **kwargs):
        config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

        # ---------------------------------------------------------
        # 1) Actualizar presupuesto diario
        # ---------------------------------------------------------
        nuevo_presupuesto = request.POST.get("presupuesto_diario")
        if nuevo_presupuesto:
            try:
                config.presupuesto_diario = to_decimal(
                    nuevo_presupuesto, config.presupuesto_diario
                )
                config.save()
                messages.success(request, "Presupuesto actualizado.")
            except InvalidOperation:
                messages.error(request, "El valor ingresado no es válido.")

            return redirect("finanzas:dashboard")

        # ---------------------------------------------------------
        # Obtener o crear el registro de hoy
        # ---------------------------------------------------------
        try:
            registro = RegistroFinanciero.objects.get(
                user=request.user,
                fecha=date.today()
            )
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        # ---------------------------------------------------------
        # 2) Fijar / desfijar valores
        # ---------------------------------------------------------
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")

            # Crear registro si no existe
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

            # Valor a fijar
            if tipo == "sobrante":
                valor = registro.sobrante_monetario
            else:
                valor_raw = request.POST.get(tipo)
                valor = to_decimal(valor_raw)

                if valor <= 0:
                    messages.warning(
                        request, "⚠️ Debe ingresar un monto positivo."
                    )
                    return redirect("finanzas:dashboard")

            # Asignar campos
            campo_valor = tipo if tipo != "sobrante" else "sobrante_monetario"
            campo_fijo = f"{tipo}_fijo"

            setattr(registro, campo_fijo, not getattr(registro, campo_fijo))
            setattr(registro, campo_valor, valor)

            # Recalcular sobrante si no está fijo
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos,
                )

            registro.save()
            messages.success(request, f"{tipo.capitalize()} actualizado.")
            return redirect("finanzas:dashboard")

        # ---------------------------------------------------------
        # 3) Guardar todos los valores del día
        # ---------------------------------------------------------
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

            # Recalcular sobrante si NO está fijo
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

            registro.completado = True
            registro.save()

            messages.success(request, "Registro guardado exitosamente.")
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    # =====================================================
    # GET — contexto
    # =====================================================
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config, _ = ConfigFinanciera.objects.get_or_create(
            user=self.request.user
        )

        # Valores de presupuesto
        presupuesto_val = int(config.presupuesto_diario)
        context["presupuesto_diario"] = str(presupuesto_val)
        context["presupuesto_mostrar"] = str(presupuesto_val)

        # =======================================
        # 1️⃣ LISTA REAL DE REGISTROS PENDIENTES
        # (FILTRADOS POR FECHA INICIAL)
        # =======================================
        fecha_inicio = config.fecha_inicio_registros or date.today()

        dias_pendientes = RegistroFinanciero.objects.filter(
            user=self.request.user,
            completado=False,
            fecha__gte=fecha_inicio
        ).order_by("fecha")

        context["dias_pendientes"] = dias_pendientes
        context["hay_dias_pendientes"] = dias_pendientes.exists()

        # =======================================
        # 2️⃣ Sistema previo
        # =======================================
        pendientes, mensaje_pendientes = obtener_dias_pendientes(
            self.request.user
        )

        pendientes_limpios = [d for d in pendientes if d]
        pendientes_limpios.sort()

        context["pendientes"] = pendientes_limpios
        context["hay_pendientes"] = len(pendientes_limpios) > 0
        context["mensaje_pendientes"] = mensaje_pendientes

        # =======================================
        # Registro de hoy
        # =======================================
        try:
            registro = RegistroFinanciero.objects.get(
                user=self.request.user,
                fecha=date.today()
            )
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        def dec(v):
            try:
                return str(int(v))
            except:
                return "0"

        if existe_registro:

            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos,
                )
                registro.save()

            context["valor_alimento"] = dec(registro.alimento)
            context["valor_productos"] = dec(registro.productos)
            context["valor_ahorro_y_deuda"] = dec(registro.ahorro_y_deuda)
            context["valor_sobrante"] = dec(registro.sobrante_monetario)

        else:
            context["valor_alimento"] = "0"
            context["valor_productos"] = "0"
            context["valor_ahorro_y_deuda"] = "0"
            context["valor_sobrante"] = str(presupuesto_val)

        registros = RegistroFinanciero.objects.filter(
            user=self.request.user
        ).order_by("-fecha")

        context.update({
            "config": config,
            "registro": registro,
            "existe_registro": existe_registro,
            "dia_completado": registro.completado if registro else False,
            "registros": registros,
            "total_gastado": sum(r.gasto_total for r in registros),
            "total_sobrante": sum(r.sobrante_monetario for r in registros),
            "hoy": date.today(),
        })

        return context