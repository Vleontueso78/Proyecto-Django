from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from datetime import date, timedelta
from ..models import RegistroFinanciero

@login_required
def configurar_calendario(request):
    if request.method == "POST":
        fecha_inicio = request.POST.get("fecha_inicio")

        if fecha_inicio:
            fecha_inicio = date.fromisoformat(fecha_inicio)
            hoy = date.today()

            # Generar días desde fecha_inicio hasta hoy
            actual = fecha_inicio
            while actual <= hoy:
                RegistroFinanciero.objects.get_or_create(
                    user=request.user,
                    fecha=actual,
                    defaults={
                        "para_gastar_dia": 0,
                        "alimento": 0,
                        "productos": 0,
                        "ahorro_y_deuda": 0,
                        "sobrante_monetario": 0,
                        "alimento_fijo": False,
                        "productos_fijo": False,
                        "ahorro_y_deuda_fijo": False,
                        "sobrante_fijo": False,
                        "completado": False,
                    },
                )
                actual += timedelta(days=1)

        return redirect("finanzas:dashboard")

    return render(request, "finanzas/configurar_calendario.html")