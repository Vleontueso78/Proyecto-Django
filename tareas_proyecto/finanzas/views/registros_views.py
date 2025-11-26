from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages

from datetime import date, timedelta

from ..calculo_sobrante.calculadora import calcular_sobrante
from ..models import RegistroFinanciero, ConfigFinanciera
from ..forms import RegistroFinancieroForm


# ======================================================
#   FUNCIONES AUXILIARES — DÍAS PENDIENTES
# ======================================================

def obtener_dias_pendientes(usuario):
    """
    Calcula desde el último día guardado hasta hoy
    y devuelve solo los días SIN registrar.
    """
    hoy = date.today()

    # Último registro guardado por el usuario
    ultimo = RegistroFinanciero.objects.filter(user=usuario).order_by("-fecha").first()

    if ultimo:
        inicio = ultimo.fecha + timedelta(days=1)
    else:
        inicio = hoy  # si nunca registró nada

    pendientes = []
    dia = inicio

    # Crea lista de días faltantes hasta hoy
    while dia <= hoy:
        existe = RegistroFinanciero.objects.filter(user=usuario, fecha=dia).exists()
        if not existe:
            pendientes.append(dia)
        dia += timedelta(days=1)

    return pendientes


# ======================================================
#   VISTA: LISTA DE DÍAS PENDIENTES
# ======================================================

def registros_pendientes(request):
    pendientes = obtener_dias_pendientes(request.user)

    if not pendientes:
        return render(request, "finanzas/registros/registros_lista.html", {
            "pendientes": [],
            "mensaje": "✔ No hay días pendientes. Todo está completo."
        })

    return render(request, "finanzas/registros/registros_lista.html", {
        "pendientes": pendientes
    })


# ======================================================
#   VISTA: COMPLETAR EL SIGUIENTE DÍA PENDIENTE
# ======================================================

def completar_pendiente(request):
    pendientes = obtener_dias_pendientes(request.user)

    # Si no hay pendientes → volvemos a la lista normal
    if not pendientes:
        return redirect("finanzas:registros")

    dia_objetivo = pendientes[0]

    # Config financiera del usuario (valores por defecto)
    config = ConfigFinanciera.objects.get(user=request.user)

    # Crear o recuperar registro del día
    registro, creado = RegistroFinanciero.objects.get_or_create(
        user=request.user,
        fecha=dia_objetivo,
        defaults={
            "para_gastar_dia": config.presupuesto_diario,
            "alimento": 0,
            "productos": 0,
            "ahorro_y_deuda": 0,
        }
    )

    if request.method == "POST":
        p = float(request.POST.get("para_gastar_dia") or config.presupuesto_diario)
        a = float(request.POST.get("alimento") or 0)
        pr = float(request.POST.get("productos") or 0)
        ad = float(request.POST.get("ahorro_y_deuda") or 0)

        registro.para_gastar_dia = p
        registro.alimento = a
        registro.productos = pr
        registro.ahorro_y_deuda = ad

        # Si no tiene sobrante fijo → recalcular
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        registro.save()

        # Redirigir al siguiente pendiente automáticamente
        return redirect("finanzas:completar_pendiente")

    return render(request, "finanzas/registros/registro_editar.html", {
        "registro": registro,
        "config": config,
        "defaults": {
            "para_gastar_dia": config.presupuesto_diario,
            "alimento": registro.alimento,
            "productos": registro.productos,
            "ahorro_y_deuda": registro.ahorro_y_deuda,
        },
        "form_values": {
            "para_gastar_dia": registro.para_gastar_dia,
            "alimento": registro.alimento,
            "productos": registro.productos,
            "ahorro_y_deuda": registro.ahorro_y_deuda,
        },
    })


# ======================================================
#   LISTA DE REGISTROS
# ======================================================

class RegistroListView(LoginRequiredMixin, ListView):
    model = RegistroFinanciero
    template_name = "finanzas/registros/registros.html"
    context_object_name = "registros"

    def get_queryset(self):
        return RegistroFinanciero.objects.filter(
            user=self.request.user
        ).order_by('-fecha')


# ======================================================
#   CREAR REGISTRO (MANUAL)
# ======================================================

class RegistroCreateView(LoginRequiredMixin, CreateView):
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
        pr = form.cleaned_data.get("productos")
        ad = form.cleaned_data.get("ahorro_y_deuda")

        form.instance.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        return super().form_valid(form)


# ======================================================
#   EDITAR REGISTRO EXISTENTE
# ======================================================

def editar_registro(request, pk):
    registro = get_object_or_404(RegistroFinanciero, pk=pk, user=request.user)
    config = ConfigFinanciera.objects.get(user=request.user)

    defaults = {
        "para_gastar_dia": config.presupuesto_diario,
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    form_values = {
        "para_gastar_dia": registro.para_gastar_dia or defaults["para_gastar_dia"],
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    if request.method == "POST":
        p = float(request.POST.get("para_gastar_dia") or defaults["para_gastar_dia"])
        a = float(request.POST.get("alimento") or defaults["alimento"])
        pr = float(request.POST.get("productos") or defaults["productos"])
        ad = float(request.POST.get("ahorro_y_deuda") or defaults["ahorro_y_deuda"])

        registro.para_gastar_dia = p
        registro.alimento = a
        registro.productos = pr
        registro.ahorro_y_deuda = ad

        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        registro.save()

        messages.success(request, "Registro actualizado correctamente.")
        return redirect("finanzas:registros")

    return render(request, "finanzas/registros/registro_editar.html", {
        "registro": registro,
        "config": config,
        "defaults": defaults,
        "form_values": form_values,
    })