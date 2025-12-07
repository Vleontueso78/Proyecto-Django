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

            # Generar todos los días desde fecha_inicio hasta hoy
            dias = []
            actual = fecha_inicio

            while actual <= hoy:
                dias.append(actual)
                actual += timedelta(days=1)

            # Crear registros pendientes únicamente si NO existen
            for dia in dias:
                RegistroFinanciero.objects.get_or_create(
                    user=request.user,
                    fecha=dia,
                    defaults={
                        "alimento": 0,
                        "productos": 0,
                        "ahorro_y_deuda": 0,
                        "sobrante_monetario": 0,
                        "control_financiero": False,
                        "sobrante_fijo": False,
                    },
                )

        return redirect("finanzas:dashboard")

    return render(request, "finanzas/configurar_calendario.html")