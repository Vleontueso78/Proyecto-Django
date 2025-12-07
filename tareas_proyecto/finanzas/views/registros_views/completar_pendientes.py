from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal

from ...models import RegistroFinanciero, ConfigFinanciera
from ...calculo_sobrante.calculadora import calcular_sobrante


def to_decimal(value, default=Decimal("0")):
    """
    Conversión segura a Decimal.
    Permite valores como "1200", "1.200", "1,200".
    """
    if value in [None, ""]:
        return default
    try:
        return Decimal(str(value).replace(",", "."))
    except:
        return default


# ============================================================
# NUEVA VISTA:
#   completar_pendiente_por_fecha
#   (el usuario completa el registro del día exacto)
# ============================================================
@login_required
def completar_pendiente_por_fecha(request, fecha_str):

    # Convertir YYYY-MM-DD → date
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    # Config financiera del usuario
    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

    # Buscar si ya existe un registro para ese día
    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    # Si no existe → crearlo vacío con valores iniciales
    if not registro:
        registro = RegistroFinanciero.objects.create(
            user=request.user,
            fecha=fecha,
            para_gastar_dia=config.presupuesto_diario,
            alimento=Decimal("0"),
            productos=Decimal("0"),
            ahorro_y_deuda=Decimal("0"),
        )

    # --------------------------------------------------------
    # POST → guardar los valores del día
    # --------------------------------------------------------
    if request.method == "POST":

        p = to_decimal(request.POST.get("para_gastar_dia"), config.presupuesto_diario)
        a = to_decimal(request.POST.get("alimento"))
        pr = to_decimal(request.POST.get("productos"))
        ad = to_decimal(request.POST.get("ahorro_y_deuda"))

        registro.para_gastar_dia = p
        registro.alimento = a
        registro.productos = pr
        registro.ahorro_y_deuda = ad

        # Recalcular sobrante si NO está fijo
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        registro.completado = True
        registro.save()

        # Volver a la lista de días pendientes
        return redirect("finanzas:registros_pendientes")

    # --------------------------------------------------------
    # GET → mostrar formulario
    # --------------------------------------------------------
    return render(
        request,
        "finanzas/registros/completar_pendiente.html",
        {
            "registro": registro,
            "config": config,
            "fecha": fecha,

            # Valores que se muestran en el formulario
            "defaults": {
                "para_gastar_dia": registro.para_gastar_dia,
                "alimento": registro.alimento,
                "productos": registro.productos,
                "ahorro_y_deuda": registro.ahorro_y_deuda,
            }
        }
    )