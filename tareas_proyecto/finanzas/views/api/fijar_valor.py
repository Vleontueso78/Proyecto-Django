from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from finanzas.models import ConfigFinanciera
from finanzas.models import normalizar_decimal


@login_required
@require_POST
def fijar_valor_default(request):
    """
    Fija o desfija un valor como default para días futuros.

    Espera:
    - campo: alimento | productos | ahorro_y_deuda
    - valor: decimal (opcional si se está desfijando)
    - fijo: "true" | "false"
    """

    campo = request.POST.get("campo")
    valor_raw = request.POST.get("valor")
    fijo = request.POST.get("fijo") == "true"

    mapping = {
        "alimento": (
            "default_alimento",
            "default_alimento_fijo",
        ),
        "productos": (
            "default_productos",
            "default_productos_fijo",
        ),
        "ahorro_y_deuda": (
            "default_ahorro_y_deuda",
            "default_ahorro_y_deuda_fijo",
        ),
    }

    if campo not in mapping:
        return JsonResponse(
            {"ok": False, "error": "Campo inválido"},
            status=400
        )

    campo_valor, campo_fijo = mapping[campo]

    config, _ = ConfigFinanciera.objects.get_or_create(
        user=request.user
    )

    # -----------------------------------------
    # Normalizar valor (si viene)
    # -----------------------------------------
    if valor_raw not in (None, "",):
        valor = normalizar_decimal(
            valor_raw,
            default=getattr(config, campo_valor)
        )

        if valor < 0:
            return JsonResponse(
                {
                    "ok": False,
                    "error": "El valor no puede ser negativo",
                },
                status=400
            )

        setattr(config, campo_valor, valor)

    # -----------------------------------------
    # Fijar / desfijar
    # -----------------------------------------
    setattr(config, campo_fijo, fijo)
    config.save()

    return JsonResponse({
        "ok": True,
        "campo": campo,
        "fijo": fijo,
        "valor": str(getattr(config, campo_valor)),
    })