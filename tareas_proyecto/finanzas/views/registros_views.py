from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from ..calculo_sobrante.calculadora import calcular_sobrante

from ..models import RegistroFinanciero, ConfigFinanciera
from ..forms import RegistroFinancieroForm
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages


# ===========================
#   REGISTROS FINANCIEROS
# ===========================
class RegistroListView(LoginRequiredMixin, ListView):
    """Lista de registros financieros del usuario."""
    model = RegistroFinanciero
    template_name = "finanzas/registros/registros.html"
    context_object_name = "registros"

    def get_queryset(self):
        return RegistroFinanciero.objects.filter(
            user=self.request.user
        ).order_by('-fecha')


class RegistroCreateView(LoginRequiredMixin, CreateView):
    """Formulario para crear un nuevo registro financiero."""
    model = RegistroFinanciero
    form_class = RegistroFinancieroForm
    template_name = "finanzas/crear_registro.html"
    success_url = reverse_lazy("finanzas:registros")

    def get_initial(self):
        initial = super().get_initial()
        config = ConfigFinanciera.objects.get(user=self.request.user)
        initial["para_gastar_dia"] = config.presupuesto_diario
        return initial

    def form_valid(self, form):
        form.instance.user = self.request.user

        p = form.cleaned_data.get("para_gastar_dia")
        a = form.cleaned_data.get("alimento")
        ad = form.cleaned_data.get("ahorro_y_deuda")
        pr = form.cleaned_data.get("productos")

        form.instance.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        return super().form_valid(form)


# ===========================
#   EDITAR REGISTRO
# ===========================
def editar_registro(request, pk):
    registro = get_object_or_404(RegistroFinanciero, pk=pk, user=request.user)

    config = ConfigFinanciera.objects.get(user=request.user)

    # Valores por defecto del panel
    defaults = {
        "para_gastar_dia": config.presupuesto_diario,
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    # Valores que se mostrarán en el formulario
    form_values = {
        "para_gastar_dia": registro.para_gastar_dia or defaults["para_gastar_dia"],
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    if request.method == "POST":
        para_gastar_dia = float(request.POST.get("para_gastar_dia") or defaults["para_gastar_dia"])
        alimento = float(request.POST.get("alimento") or defaults["alimento"])
        productos = float(request.POST.get("productos") or defaults["productos"])
        ahorro_y_deuda = float(request.POST.get("ahorro_y_deuda") or defaults["ahorro_y_deuda"])

        registro.para_gastar_dia = para_gastar_dia
        registro.alimento = alimento
        registro.productos = productos
        registro.ahorro_y_deuda = ahorro_y_deuda

        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(
                para_gastar_dia,
                alimento,
                ahorro_y_deuda,
                productos
            )

        registro.save()

        messages.success(request, "Registro actualizado correctamente.")
        return redirect("finanzas:registros")

    return render(request, "finanzas/registros/registro_editar.html", {
        "registro": registro,
        "config": config,
        "defaults": defaults,
        "form_values": form_values,
    })