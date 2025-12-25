from datetime import datetime
from decimal import Decimal

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from ...models import RegistroFinanciero, ConfigFinanciera


@login_required
def detalle_dia(request, fecha_str):
    # --------------------------------
    # Convertir string a date
    # --------------------------------
    fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()

    # --------------------------------
    # Presupuesto diario global (dashboard)
    # --------------------------------
    config, _ = ConfigFinanciera.objects.get_or_create(
        user=request.user
    )
    presupuesto_diario = config.presupuesto_diario or Decimal("0")

    # --------------------------------
    # Buscar registro del día
    # --------------------------------
    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    # ==========================
    # DÍA PENDIENTE (NO EXISTE)
    # ==========================
    if not registro:

        if request.method == "POST":
            RegistroFinanciero.objects.create(
                user=request.user,
                fecha=fecha,
                para_gastar_dia=request.POST.get("para_gastar_dia") or presupuesto_diario,
                alimento=request.POST.get("alimento") or 0,
                productos=request.POST.get("productos") or 0,
                ahorro_y_deuda=request.POST.get("ahorro_y_deuda") or 0,
                completado=True,
            )

            return redirect(
                "finanzas:detalle_dia",
                fecha_str=fecha_str
            )

        # Registro "virtual" para mostrar valores por defecto
        registro_virtual = {
            "para_gastar_dia": presupuesto_diario,
            "alimento": Decimal("0"),
            "productos": Decimal("0"),
            "ahorro_y_deuda": Decimal("0"),
        }

        return render(request, "finanzas/detalle_dia.html", {
            "fecha": fecha,
            "registro": registro_virtual,
            "presupuesto_diario": presupuesto_diario,
            "es_pendiente": True,
        })

    # ==========================
    # DÍA EXISTENTE
    # ==========================
    return render(request, "finanzas/detalle_dia.html", {
        "fecha": fecha,
        "registro": registro,
        "presupuesto_diario": presupuesto_diario,
        "es_pendiente": False,
    })