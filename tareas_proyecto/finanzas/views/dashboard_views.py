from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation

from ..models import RegistroFinanciero, ObjetivoFinanciero, ConfigFinanciera
from ..forms import RegistroFinancieroForm, ObjetivoFinancieroForm

# 🔥 Import centralizado del cálculo de sobrante
from ..calculo_sobrante.calculadora import calcular_sobrante


class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    """
    Panel financiero.
    Nota importante: NO se crea automáticamente el registro del día en GET.
    El registro se crea solamente cuando el usuario lo guarda (guardar_todo).
    """
    template_name = "finanzas/dashboard.html"

    # -------------------------------------------------
    # PROCESA POST
    # -------------------------------------------------
    def post(self, request, *args, **kwargs):
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

        # -------- 2️⃣ Intentar obtener registro de hoy (si existe) ----------
        try:
            registro = RegistroFinanciero.objects.get(user=request.user, fecha=date.today())
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        # -------- 3️⃣ FIJAR/DESFIJAR ----------
        if "fijar" in request.POST:
            # Si no existe registro, no permitimos fijar (evita crear registros automáticos)
            if not existe_registro:
                messages.warning(request, "Primero guardá el registro del día para poder fijar valores.")
                return redirect("finanzas:dashboard")

            tipo = request.POST.get("tipo")
            valor = request.POST.get(tipo) or request.POST.get("valor")

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

            campo_valor = tipo if tipo != "sobrante" else "sobrante_monetario"
            campo_fijo = f"{tipo}_fijo" if tipo != "sobrante" else "sobrante_fijo"

            setattr(registro, campo_valor, valor_decimal)
            actual = getattr(registro, campo_fijo)
            setattr(registro, campo_fijo, not actual)

            # Recalcular sobrante cuando corresponda
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos
                )

            registro.save()
            estado = "fijado" if getattr(registro, campo_fijo) else "desfijado"
            messages.success(request, f"{tipo.capitalize()} {estado} correctamente.")
            return redirect("finanzas:dashboard")

        # -------- 4️⃣ GUARDAR TODOS LOS GASTOS ----------
        if "guardar_todo" in request.POST:
            # Obtener valores desde POST o por defecto
            def to_decimal_or_zero(value, default=Decimal("0")):
                try:
                    if value is None or value == "":
                        return default
                    return Decimal(str(value).replace(",", "."))
                except (InvalidOperation, ValueError):
                    return default

            p_raw = request.POST.get("para_gastar_dia")
            a_raw = request.POST.get("alimento")
            pr_raw = request.POST.get("productos")
            ad_raw = request.POST.get("ahorro_y_deuda")

            p = to_decimal_or_zero(p_raw, config.presupuesto_diario)
            a = to_decimal_or_zero(a_raw, Decimal("0"))
            pr = to_decimal_or_zero(pr_raw, Decimal("0"))
            ad = to_decimal_or_zero(ad_raw, Decimal("0"))

            # Si no existe registro - lo creamos ahora (usuario eligió guardar)
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
                # Actualizar registro existente
                registro.para_gastar_dia = p
                registro.alimento = a
                registro.productos = pr
                registro.ahorro_y_deuda = ad

            # Recalcular sobrante si no está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos
                )

            # Marcar día como completado (ya fue guardado por el usuario)
            registro.completado = True
            registro.save()

            messages.success(request, "💾 Datos guardados correctamente.")
            # Redirigir al dashboard (o a la lista si preferís)
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    # -------------------------------------------------
    # CONTEXTO (GET)
    # -------------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        config, _ = ConfigFinanciera.objects.get_or_create(user=self.request.user)

        # Intentamos obtener el registro del día si existe; NO lo creamos automáticamente
        try:
            registro = RegistroFinanciero.objects.get(user=self.request.user, fecha=date.today())
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        # Si existe registro, recalculamos si hace falta y formateamos valores
        if existe_registro:
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos
                )
                registro.save()

            def dec(v):
                return format(v, "f").replace(",", ".")

            context["valor_alimento"] = dec(registro.alimento)
            context["valor_ahorro_y_deuda"] = dec(registro.ahorro_y_deuda)
            context["valor_sobrante"] = dec(registro.sobrante_monetario)
        else:
            # Valores por defecto (para mostrar en inputs, pero NO crear registro)
            def dec(v):
                return format(v, "f").replace(",", ".")

            context["valor_alimento"] = dec(Decimal("0"))
            context["valor_ahorro_y_deuda"] = dec(Decimal("0"))
            # sobrante por defecto = presupuesto (sin gastos)
            context["valor_sobrante"] = dec(config.presupuesto_diario)

        # -------- 4️⃣ DATOS GENERALES ----------
        registros = RegistroFinanciero.objects.filter(user=self.request.user).order_by("-fecha")

        context.update({
            "config": config,
            "registro": registro,                 # None si no existe
            "existe_registro": existe_registro,   # útil para template
            "dia_completado": registro.completado if registro else False,
            "registros": registros,
            "total_gastado": sum(r.gasto_total for r in registros),
            "total_sobrante": sum(r.sobrante_efectivo for r in registros),
            "hoy": date.today(),
        })

        return context