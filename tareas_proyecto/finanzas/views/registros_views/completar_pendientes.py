from django.shortcuts import redirect, render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from decimal import Decimal

from ...models import RegistroFinanciero, ConfigFinanciera
from ...calculo_sobrante.calculadora import calcular_sobrante


# ============================================================
# Función utilitaria → convierte valores a Decimal de forma segura
# ============================================================
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
# VISTA PRINCIPAL:
#   completar_pendiente_por_fecha
# ============================================================
@login_required
def completar_pendiente_por_fecha(request, fecha_str):
    """
    Permite completar un día pendiente según la fecha seleccionada desde el dashboard.
    Si el registro no existe, se crea automáticamente con los valores base.
    """

    # Convertir string YYYY-MM-DD → date
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    # Config financiera del usuario
    config, _ = ConfigFinanciera.objects.get_or_create(user=request.user)

    # Buscar registro del día
    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    # Si no existe → se crea vacío automáticamente
    if not registro:
        registro = RegistroFinanciero.objects.create(
            user=request.user,
            fecha=fecha,
            para_gastar_dia=config.presupuesto_diario,
            alimento=Decimal("0"),
            productos=Decimal("0"),
            ahorro_y_deuda=Decimal("0"),
            sobrante_monetario=Decimal("0"),
            completado=False,
        )

    # --------------------------------------------------------
    # POST → guardar cambios del formulario
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

        # Recalcular sobrante si no está bloqueado
        if not registro.sobrante_fijo:
            registro.sobrante_monetario = calcular_sobrante(p, a, ad, pr)

        # Marcar como completado
        registro.completado = True
        registro.save()

        return redirect("finanzas:registros_pendientes")

    # --------------------------------------------------------
    # GET → mostrar el formulario con valores actuales
    # --------------------------------------------------------
    return render(
        request,
        "finanzas/registros/completar_pendiente.html",
        {
            "registro": registro,
            "config": config,
            "fecha": fecha,
            "defaults": {
                "para_gastar_dia": registro.para_gastar_dia,
                "alimento": registro.alimento,
                "productos": registro.productos,
                "ahorro_y_deuda": registro.ahorro_y_deuda,
            }
        }
    )