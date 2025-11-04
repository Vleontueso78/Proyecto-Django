from django.views.generic import ListView, CreateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation
from .models import RegistroFinanciero, ObjetivoFinanciero, ConfigFinanciera
from .forms import RegistroFinancieroForm, ObjetivoFinancieroForm


# ===========================
#   DASHBOARD PRINCIPAL
# ===========================
class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    """Vista principal del panel financiero."""
    template_name = "finanzas/dashboard.html"

    def post(self, request, *args, **kwargs):
        config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

        # --- 1️⃣ Modificar presupuesto diario ---
        nuevo_presupuesto = request.POST.get("presupuesto_diario")
        if nuevo_presupuesto:
            try:
                config.presupuesto_diario = Decimal(nuevo_presupuesto)
                config.save()
                messages.success(request, "Presupuesto diario actualizado correctamente.")
            except (ValueError, InvalidOperation):
                messages.error(request, "El valor ingresado no es válido.")
            return redirect("finanzas:dashboard")

        # --- 2️⃣ Obtener o crear el registro de hoy ---
        registro, _ = RegistroFinanciero.objects.get_or_create(
            user=request.user,
            fecha=date.today(),
            defaults={"para_gastar_dia": config.presupuesto_diario},
        )

        # --- 3️⃣ Fijar o desfijar gasto individual ---
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")
            valor = request.POST.get(tipo, None)

            if not valor or valor.strip() == "":
                messages.warning(request, "⚠️ Agregar monto válido antes de fijar.")
                return redirect("finanzas:dashboard")

            try:
                valor_decimal = Decimal(valor)
            except (ValueError, InvalidOperation):
                messages.warning(request, "⚠️ El monto ingresado no es válido.")
                return redirect("finanzas:dashboard")

            if valor_decimal <= 0:
                messages.warning(request, "⚠️ El monto debe ser positivo.")
                return redirect("finanzas:dashboard")

            campo_valor = tipo if tipo != "sobrante" else "sobrante_monetario"
            campo_fijo = f"{tipo}_fijo" if tipo != "sobrante" else "sobrante_fijo"

            setattr(registro, campo_valor, valor_decimal)
            actual = getattr(registro, campo_fijo)
            setattr(registro, campo_fijo, not actual)

            # ✅ Solo recalcula sobrante si no está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = (
                    Decimal(registro.para_gastar_dia)
                    - Decimal(registro.alimento)
                    - Decimal(registro.ahorro_y_deuda)
                )

            registro.save()
            estado = "fijado" if getattr(registro, campo_fijo) else "desfijado"
            messages.success(request, f"{tipo.capitalize()} {estado} correctamente.")
            return redirect("finanzas:dashboard")

        # --- 4️⃣ Guardar todos los gastos ---
        if "guardar_todo" in request.POST:
            for campo, modelo in [
                ("alimento", "alimento"),
                ("ahorro_y_deuda", "ahorro_y_deuda"),
            ]:
                valor = request.POST.get(campo)
                try:
                    setattr(registro, modelo, Decimal(valor or "0"))
                except (ValueError, InvalidOperation):
                    pass

            # ✅ Solo recalcular sobrante si no está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = (
                    Decimal(registro.para_gastar_dia)
                    - Decimal(registro.alimento)
                    - Decimal(registro.ahorro_y_deuda)
                )

            registro.save()
            messages.success(request, "💾 Datos guardados correctamente.")
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config, _ = ConfigFinanciera.objects.get_or_create(user=self.request.user)

        # --- 1️⃣ Obtener o crear registro del día ---
        registro, creado = RegistroFinanciero.objects.get_or_create(
            user=self.request.user,
            fecha=date.today(),
            defaults={"para_gastar_dia": config.presupuesto_diario},
        )

        # --- 2️⃣ Copiar valores fijos del último día (solo si es nuevo) ---
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
                    "📌 Se restauraron los valores fijos del día anterior.",
                )

        # --- 3️⃣ Calcular sobrante solo si no está fijado ---
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = (
                Decimal(registro.para_gastar_dia)
                - Decimal(registro.alimento)
                - Decimal(registro.ahorro_y_deuda)
            )
            registro.save()

        # --- 4️⃣ Cargar contexto ---
        registros = RegistroFinanciero.objects.filter(user=self.request.user).order_by("-fecha")

        context.update({
            "config": config,
            "registro": registro,
            "registros": registros,
            "total_gastado": sum(r.gasto_total for r in registros),
            "total_sobrante": sum(r.sobrante_efectivo for r in registros),
            "hoy": date.today(),
        })
        return context


# ===========================
#   REGISTROS FINANCIEROS
# ===========================
class RegistroListView(LoginRequiredMixin, ListView):
    """Lista de registros financieros del usuario."""
    model = RegistroFinanciero
    template_name = "finanzas/registros.html"
    context_object_name = "registros"

    def get_queryset(self):
        return RegistroFinanciero.objects.filter(user=self.request.user).order_by('-fecha')


class RegistroCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo registro financiero."""
    model = RegistroFinanciero
    form_class = RegistroFinancieroForm
    template_name = "finanzas/crear_registro.html"
    success_url = reverse_lazy("finanzas:registros")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


# ===========================
#   OBJETIVOS FINANCIEROS
# ===========================
class ObjetivoListView(LoginRequiredMixin, ListView):
    """Lista de objetivos financieros."""
    model = ObjetivoFinanciero
    template_name = "finanzas/objetivos.html"
    context_object_name = "objetivos"

    def get_queryset(self):
        return ObjetivoFinanciero.objects.filter(user=self.request.user).order_by('-fecha_creacion')


class ObjetivoCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo objetivo financiero."""
    model = ObjetivoFinanciero
    form_class = ObjetivoFinancieroForm
    template_name = "finanzas/crear_objetivo.html"
    success_url = reverse_lazy("finanzas:objetivos")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)