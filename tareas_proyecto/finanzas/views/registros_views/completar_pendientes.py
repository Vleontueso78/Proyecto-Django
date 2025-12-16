from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime
from decimal import Decimal

from ...models import RegistroFinanciero, ConfigFinanciera
from ...calculo_sobrante.calculadora import calcular_sobrante
from .dias_pendientes import obtener_dias_pendientes


# ============================================================
# Conversión segura a Decimal
# ============================================================
def to_decimal(value, default=Decimal("0")):
    if value in [None, ""]:
        return default
    try:
        return Decimal(str(value).replace(",", "."))
    except:
        return default


# ============================================================
# Vista: Lista de días pendientes
# ============================================================
@login_required
def registros_pendientes(request):
    pendientes, mensaje = obtener_dias_pendientes(request.user)
    pendientes = sorted([d for d in pendientes if d])

    return render(
        request,
        "finanzas/registros/pendientes.html",
        {
            "pendientes": pendientes,
            "mensaje": mensaje,
        }
    )


# ============================================================
# Vista: Completar un día pendiente
# ============================================================
@login_required
def completar_pendiente_por_fecha(request, fecha_str):

    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    # ------------------------------------------------------------
    # CREACIÓN DEL REGISTRO (aplica valores fijos automáticamente)
    # ------------------------------------------------------------
    if not registro:
        registro = RegistroFinanciero.objects.create(
            user=request.user,
            fecha=fecha,
            para_gastar_dia=config.presupuesto_diario,
            alimento=config.default_alimento if config.default_alimento_fijo else Decimal("0"),
            productos=config.default_productos if config.default_productos_fijo else Decimal("0"),
            ahorro_y_deuda=config.default_ahorro_y_deuda if config.default_ahorro_y_deuda_fijo else Decimal("0"),
            sobrante_monetario=config.default_sobrante if config.default_sobrante_fijo else Decimal("0"),

            alimento_fijo=config.default_alimento_fijo,
            productos_fijo=config.default_productos_fijo,
            ahorro_y_deuda_fijo=config.default_ahorro_y_deuda_fijo,
            sobrante_fijo=config.default_sobrante_fijo,
        )

    # ------------------------------------------------------------
    # POST
    # ------------------------------------------------------------
    if request.method == "POST":

        if not registro.alimento_fijo:
            registro.alimento = to_decimal(request.POST.get("alimento"))

        if not registro.productos_fijo:
            registro.productos = to_decimal(request.POST.get("productos"))

        if not registro.ahorro_y_deuda_fijo:
            registro.ahorro_y_deuda = to_decimal(request.POST.get("ahorro_y_deuda"))

        registro.para_gastar_dia = to_decimal(
            request.POST.get("para_gastar_dia"),
            registro.para_gastar_dia
        )

        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(
                registro.para_gastar_dia,
                registro.alimento,
                registro.ahorro_y_deuda,
                registro.productos,
            )

        registro.completado = True
        registro.save()

        messages.success(
            request,
            f"✅ Registro del {fecha.strftime('%d/%m/%Y')} guardado correctamente."
        )

        return redirect("finanzas:registros_pendientes")

    # ------------------------------------------------------------
    # GET
    # ------------------------------------------------------------
    form_values = {
        "para_gastar_dia": registro.para_gastar_dia,
        "alimento": registro.alimento,
        "productos": registro.productos,
        "ahorro_y_deuda": registro.ahorro_y_deuda,
    }

    fixed_fields = {
        "alimento": registro.alimento_fijo,
        "productos": registro.productos_fijo,
        "ahorro_y_deuda": registro.ahorro_y_deuda_fijo,
    }

    return render(
        request,
        "finanzas/registros/completar_pendiente.html",
        {
            "registro": registro,
            "fecha": fecha,
            "form_values": form_values,
            "fixed_fields": fixed_fields,
        }
    )