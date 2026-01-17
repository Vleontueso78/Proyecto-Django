from datetime import datetime, date

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.contrib import messages

from ...models import (
    RegistroFinanciero,
    ConfigFinanciera,
    normalizar_decimal,
)


@login_required
def detalle_dia(request, fecha_str):
    """
    Vista de detalle y carga del registro financiero de un día específico.
    """

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

    # --------------------------------------------------------
    # 3️⃣ Validaciones de rango
    # --------------------------------------------------------
    if fecha > hoy:
        raise Http404("No se puede acceder a fechas futuras")

    if config.fecha_inicio_registros and fecha < config.fecha_inicio_registros:
        raise Http404("Fecha fuera del rango configurado")

    # --------------------------------------------------------
    # 4️⃣ Obtener o crear registro (IDEMPOTENTE)
    # --------------------------------------------------------
    registro = RegistroFinanciero.objects.filter(
        user=request.user,
        fecha=fecha
    ).first()

    if not registro:
        registro = RegistroFinanciero.objects.create(
            user=request.user,
            fecha=fecha,
            para_gastar_dia=normalizar_decimal(
                config.presupuesto_diario
            ),

            alimento=normalizar_decimal(
                config.default_alimento
                if config.default_alimento_fijo else 0
            ),
            productos=normalizar_decimal(
                config.default_productos
                if config.default_productos_fijo else 0
            ),
            ahorro_y_deuda=normalizar_decimal(
                config.default_ahorro_y_deuda
                if config.default_ahorro_y_deuda_fijo else 0
            ),

            alimento_fijo=config.default_alimento_fijo,
            productos_fijo=config.default_productos_fijo,
            ahorro_y_deuda_fijo=config.default_ahorro_y_deuda_fijo,

            completado=False,
        )

    # --------------------------------------------------------
    # 5️⃣ POST → Guardar / completar día
    # --------------------------------------------------------
    if request.method == "POST":

        if not registro.alimento_fijo:
            registro.alimento = normalizar_decimal(
                request.POST.get("alimento")
            )

        if not registro.productos_fijo:
            registro.productos = normalizar_decimal(
                request.POST.get("productos")
            )

        if not registro.ahorro_y_deuda_fijo:
            registro.ahorro_y_deuda = normalizar_decimal(
                request.POST.get("ahorro_y_deuda")
            )

        registro.para_gastar_dia = normalizar_decimal(
            request.POST.get("para_gastar_dia"),
            default=registro.para_gastar_dia
        )

        registro.completado = True
        registro.save()

        messages.success(
            request,
            f"Registro del {fecha.strftime('%d/%m/%Y')} guardado correctamente."
        )

        return redirect(
            "finanzas:detalle_dia",
            fecha_str=fecha.strftime("%Y-%m-%d")
        )

    # --------------------------------------------------------
    # 6️⃣ Render
    # --------------------------------------------------------
    return render(
        request,
        "finanzas/detalle_dia.html",
        {
            "fecha": fecha,
            "registro": registro,
            "dia_completado": registro.completado,
        }
    )