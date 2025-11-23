from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation

from ..models import RegistroFinanciero, ObjetivoFinanciero, ConfigFinanciera
from ..forms import RegistroFinancieroForm, ObjetivoFinancieroForm

# 🔥 Import centralizado del cálculo de sobrante
from ..calculo_sobrante.calculadora import calcular_sobrante


# ===========================
#   DASHBOARD PRINCIPAL
# ===========================
class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    """
    Vista principal del panel financiero.
    Muestra el presupuesto, los gastos del día y los valores fijados.
    """
    template_name = "finanzas/dashboard.html"

    # -------------------------------------------------
    # PROCESA FORMULARIOS (POST)
    # -------------------------------------------------
    def post(self, request, *args, **kwargs):
        # Config del usuario (presupuesto diario)
        config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

        # -------- 1️⃣ MODIFICAR PRESUPUESTO DIARIO ----------
        nuevo_presupuesto = request.POST.get("presupuesto_diario")
        if nuevo_presupuesto:
            try:
                config.presupuesto_diario = Decimal(nuevo_presupuesto)
                config.save()
                messages.success(request, "Presupuesto diario actualizado correctamente.")
            except (ValueError, InvalidOperation):
                messages.error(request, "El valor ingresado no es válido.")
            return redirect("finanzas:dashboard")

        # -------- 2️⃣ OBTENER O CREAR REGISTRO DEL DÍA ----------
        registro, _ = RegistroFinanciero.objects.get_or_create(
            user=request.user,
            fecha=date.today(),
            defaults={"para_gastar_dia": config.presupuesto_diario},
        )

        # -------- 3️⃣ FIJAR/DESFIJAR GASTO INDIVIDUAL ----------
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")  # alimento / ahorro / sobrante
            valor = request.POST.get(tipo) or request.POST.get("valor")

            # Validación
            if not valor or valor.strip() == "":
                messages.warning(request, "⚠️ Agregar monto válido antes de fijar.")
                return redirect("finanzas:dashboard")

            try:
                valor_decimal = Decimal(valor.replace(",", "."))
            except (ValueError, InvalidOperation):
                messages.warning(request, "⚠️ El monto ingresado no es válido.")
                return redirect("finanzas:dashboard")

            if valor_decimal <= 0:
                messages.warning(request, "⚠️ El monto debe ser positivo.")
                return redirect("finanzas:dashboard")

            # Campos del modelo
            campo_valor = tipo if tipo != "sobrante" else "sobrante_monetario"
            campo_fijo = f"{tipo}_fijo" if tipo != "sobrante" else "sobrante_fijo"

            # Alternar fijación
            setattr(registro, campo_valor, valor_decimal)
            actual = getattr(registro, campo_fijo)
            setattr(registro, campo_fijo, not actual)

            # Recalcular sobrante solo si NO está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda
                )

            registro.save()
            estado = "fijado" if getattr(registro, campo_fijo) else "desfijado"
            messages.success(request, f"{tipo.capitalize()} {estado} correctamente.")
            return redirect("finanzas:dashboard")

        # -------- 4️⃣ GUARDAR TODOS LOS GASTOS ----------
        if "guardar_todo" in request.POST:
            for campo in ["alimento", "ahorro_y_deuda"]:
                valor = request.POST.get(campo)
                try:
                    setattr(registro, campo, Decimal(valor.replace(",", ".") or "0"))
                except:
                    pass

            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda
                )

            registro.save()
            messages.success(request, "💾 Datos guardados correctamente.")
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    # -------------------------------------------------
    # CONTEXTO PARA LA PÁGINA (GET)
    # -------------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Config
        config, _ = ConfigFinanciera.objects.get_or_create(user=self.request.user)

        # Registro del día
        registro, creado = RegistroFinanciero.objects.get_or_create(
            user=self.request.user,
            fecha=date.today(),
            defaults={"para_gastar_dia": config.presupuesto_diario},
        )

        # -------- 1️⃣ COPIAR FIJOS DEL DÍA ANTERIOR ----------
        if creado:
            ultimo = (
                RegistroFinanciero.objects.filter(user=self.request.user)
                .exclude(id=registro.id)
                .order_by("-fecha")
                .first()
            )

            if ultimo:
                if ultimo.alimento_fijo:
                    registro.alimento = ultimo.alimento
                    registro.alimento_fijo = True
                if ultimo.ahorro_y_deuda_fijo:
                    registro.ahorro_y_deuda = ultimo.ahorro_y_deuda
                    registro.ahorro_y_deuda_fijo = True
                if ultimo.sobrante_fijo:
                    registro.sobrante_monetario = ultimo.sobrante_monetario
                    registro.sobrante_fijo = True

                registro.save()

                messages.info(
                    self.request,
                    "📌 Se restauraron los valores fijos del día anterior."
                )

        # -------- 2️⃣ RE-CALCULAR SOBRANTE (si no está fijado) ----------
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(
                registro.para_gastar_dia,
                registro.alimento,
                registro.ahorro_y_deuda
            )
            registro.save()

        # -------- 3️⃣ FORMATEO PARA INPUTS ----------
        def dec(v):
            return format(v, "f").replace(",", ".")

        context["valor_alimento"] = dec(registro.alimento)
        context["valor_ahorro_y_deuda"] = dec(registro.ahorro_y_deuda)
        context["valor_sobrante"] = dec(registro.sobrante_monetario)

        # -------- 4️⃣ DATOS GENERALES ----------
        registros = RegistroFinanciero.objects.filter(
            user=self.request.user
        ).order_by("-fecha")

        context.update({
            "config": config,
            "registro": registro,
            "registros": registros,
            "total_gastado": sum(r.gasto_total for r in registros),
            "total_sobrante": sum(r.sobrante_efectivo for r in registros),
            "hoy": date.today(),
        })

        return context