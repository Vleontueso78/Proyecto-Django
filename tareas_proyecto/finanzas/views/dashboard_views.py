from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from datetime import date
from decimal import Decimal, InvalidOperation

from ..models import RegistroFinanciero, ConfigFinanciera
from ..calculo_sobrante.calculadora import calcular_sobrante
from ..views.registros_views import obtener_dias_pendientes


class FinanzasDashboardView(LoginRequiredMixin, TemplateView):
    template_name = "finanzas/dashboard.html"

    # -------------------------------------------------
    # POST
    # -------------------------------------------------
    def post(self, request, *args, **kwargs):
        config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

        # 1) actualizar presupuesto
        nuevo_presupuesto = request.POST.get("presupuesto_diario")
        if nuevo_presupuesto:
            try:
                config.presupuesto_diario = Decimal(nuevo_presupuesto.replace(",", "."))
                config.save()
                messages.success(request, "Presupuesto diario actualizado correctamente.")
            except (ValueError, InvalidOperation):
                messages.error(request, "El valor ingresado no es válido.")
            return redirect("finanzas:dashboard")

        # verificar si ya existe registro de hoy
        try:
            registro = RegistroFinanciero.objects.get(user=request.user, fecha=date.today())
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        # 2) fijar / desfijar valores
        if "fijar" in request.POST:
            tipo = request.POST.get("tipo")

            # crear registro solo si ES NECESARIO fijar algo
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

            # obtener valor
            if tipo == "sobrante":
                valor_decimal = registro.sobrante_monetario
            else:
                valor_raw = request.POST.get(tipo)
                if not valor_raw:
                    messages.warning(request, "⚠️ Agregar monto válido antes de fijar.")
                    return redirect("finanzas:dashboard")
                try:
                    valor_decimal = Decimal(valor_raw.replace(",", "."))
                except:
                    messages.warning(request, "⚠️ Valor inválido.")
                    return redirect("finanzas:dashboard")

            if valor_decimal <= 0:
                messages.warning(request, "⚠️ Debe ingresar un monto positivo.")
                return redirect("finanzas:dashboard")

            campo_valor = tipo if tipo != "sobrante" else "sobrante_monetario"
            campo_fijo = f"{tipo}_fijo"

            # alternar fijación
            actual = getattr(registro, campo_fijo)
            setattr(registro, campo_fijo, not actual)
            setattr(registro, campo_valor, valor_decimal)

            # recalcular sobrante si no está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    registro.para_gastar_dia,
                    registro.alimento,
                    registro.ahorro_y_deuda,
                    registro.productos,
                )

            registro.save()
            messages.success(request, f"{tipo.capitalize()} fijado correctamente.")

            return redirect("finanzas:dashboard")

        # 3) GUARDAR TODOS LOS GASTOS (marca completado)
        if "guardar_todo" in request.POST:

            def to_decimal(v, default=Decimal("0")):
                try:
                    if not v:
                        return default
                    return Decimal(v.replace(",", "."))
                except:
                    return default

            p = to_decimal(request.POST.get("para_gastar_dia"), config.presupuesto_diario)
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

            # calcular sobrante si no está fijado
            if not registro.sobrante_fijo:
                registro.sobrante_monetario = calcular_sobrante(
                    p, a, ad, pr
                )

            registro.completado = True
            registro.save()

            messages.success(request, "Registro del día guardado correctamente.")
            return redirect("finanzas:dashboard")

        return redirect("finanzas:dashboard")

    # -------------------------------------------------
    # GET - contexto
    # -------------------------------------------------
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        config, _ = ConfigFinanciera.objects.get_or_create(user=self.request.user)

        pendientes = obtener_dias_pendientes(self.request.user)

        # registro de HOY (solo si existe)
        try:
            registro = RegistroFinanciero.objects.get(user=self.request.user, fecha=date.today())
            existe_registro = True
        except RegistroFinanciero.DoesNotExist:
            registro = None
            existe_registro = False

        def dec(v):
            return format(v, "f")

        # valores para mostrar en inputs
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
            # día sin registro → valores por defecto
            context["valor_alimento"] = "0"
            context["valor_productos"] = "0"
            context["valor_ahorro_y_deuda"] = "0"
            context["valor_sobrante"] = dec(config.presupuesto_diario)

        # para resumen
        registros = RegistroFinanciero.objects.filter(user=self.request.user).order_by("-fecha")

        context.update({
            "config": config,
            "pendientes": pendientes,
            "hay_pendientes": len(pendientes) > 0,
            "registro": registro,
            "existe_registro": existe_registro,
            "dia_completado": registro.completado if registro else False,
            "registros": registros,
            "total_gastado": sum(r.gasto_total for r in registros),
            "total_sobrante": sum(r.sobrante_efectivo for r in registros),
            "hoy": date.today(),
        })

        return context
