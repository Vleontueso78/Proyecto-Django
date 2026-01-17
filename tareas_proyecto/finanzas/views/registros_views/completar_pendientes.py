from datetime import datetime, date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import Http404

from ...models import (
    RegistroFinanciero,
    ConfigFinanciera,
    normalizar_decimal,
)


# ============================================================
# Vista: Completar un día pendiente
# ============================================================
@login_required
def completar_pendiente_por_fecha(request, fecha_str):
    # --------------------------------------------------------
    # 1️⃣ Validar fecha
    # --------------------------------------------------------
    try:
        fecha = datetime.strptime(fecha_str, "%Y-%m-%d").date()
    except ValueError:
        raise Http404("Fecha inválida")

    hoy = date.today()

    # --------------------------------------------------------
    # 2️⃣ Configuración financiera
    # --------------------------------------------------------
    config, _ = ConfigFinanciera.objects.get_or_create(
        user=request.user
    )

    if not config.fecha_inicio_registros:
        messages.warning(
            request,
            "Debes configurar una fecha de inicio primero."
        )
        return redirect("finanzas:dashboard")

    if fecha < config.fecha_inicio_registros or fecha > hoy:
        raise Http404("Fecha fuera de rango")

    # --------------------------------------------------------
    # 3️⃣ Buscar registro existente
    # --------------------------------------------------------
    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    # ❌ Si ya está completado, no es pendiente
    if registro and registro.completado:
        messages.info(
            request,
            "Este día ya fue completado."
        )
        return redirect("finanzas:registros_pendientes")

    # --------------------------------------------------------
    # 4️⃣ Crear registro si no existe (idempotente)
    # --------------------------------------------------------
    if not registro:
        defaults = config.get_defaults_registro()
        defaults["completado"] = False

        registro = RegistroFinanciero.objects.create(
            user=request.user,
            fecha=fecha,
            **defaults
        )

    # --------------------------------------------------------
    # 5️⃣ POST → Guardar datos
    # --------------------------------------------------------
    if request.method == "POST":

        if not registro.alimento_fijo:
            registro.alimento = normalizar_decimal(
                request.POST.get("alimento"),
                default=registro.alimento,
            )

        if not registro.productos_fijo:
            registro.productos = normalizar_decimal(
                request.POST.get("productos"),
                default=registro.productos,
            )

        if not registro.ahorro_y_deuda_fijo:
            registro.ahorro_y_deuda = normalizar_decimal(
                request.POST.get("ahorro_y_deuda"),
                default=registro.ahorro_y_deuda,
            )

        registro.para_gastar_dia = normalizar_decimal(
            request.POST.get("para_gastar_dia"),
            default=registro.para_gastar_dia,
        )

        registro.completado = True
        registro.save()

        messages.success(
            request,
            f"✅ Registro del {fecha.strftime('%d/%m/%Y')} guardado correctamente."
        )

        return redirect("finanzas:registros_pendientes")

    # --------------------------------------------------------
    # 6️⃣ GET → Mostrar formulario
    # --------------------------------------------------------
    return render(
        request,
        "finanzas/registros/completar_pendiente.html",
        {
            "registro": registro,
            "fecha": fecha,
            "form_values": {
                "para_gastar_dia": registro.para_gastar_dia,
                "alimento": registro.alimento,
                "productos": registro.productos,
                "ahorro_y_deuda": registro.ahorro_y_deuda,
            },
            "fixed_fields": {
                "alimento": registro.alimento_fijo,
                "productos": registro.productos_fijo,
                "ahorro_y_deuda": registro.ahorro_y_deuda_fijo,
            },
        }
    )