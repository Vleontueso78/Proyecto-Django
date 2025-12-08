from decimal import Decimal, InvalidOperation
from django.contrib.auth import get_user_model
from datetime import date

from ..models import RegistroFinanciero

User = get_user_model()


def verificar_registros_financieros():
    print("\n=== Verificador de Registros Financieros ===\n")

    total = RegistroFinanciero.objects.count()
    print(f"Total registros: {total}")

    errores = []
    usuarios = User.objects.all()

    for user in usuarios:
        registros = RegistroFinanciero.objects.filter(user=user).order_by("fecha")

        # -------------------------------------------------------
        # 1) Fechas duplicadas por usuario
        # -------------------------------------------------------
        fechas_vistas = set()
        for r in registros:
            if r.fecha in fechas_vistas:
                errores.append(f"[{user.username}] Duplicado en fecha {r.fecha}")
            fechas_vistas.add(r.fecha)

        for r in registros:
            # -------------------------------------------------------
            # 2) Validación de tipo numérico seguro
            # -------------------------------------------------------
            for campo in ["para_gastar_dia", "alimento", "productos", "ahorro_y_deuda", "sobrante_monetario"]:
                valor = getattr(r, campo)
                try:
                    Decimal(valor)
                except (InvalidOperation, TypeError):
                    errores.append(f"[{user.username}] {campo} contiene dato inválido → {valor}")

            # -------------------------------------------------------
            # 3) Valores negativos imposibles
            # -------------------------------------------------------
            if r.para_gastar_dia < 0:
                errores.append(f"[{user.username}] para_gastar_dia negativo en {r.fecha}")

            if r.alimento < 0 or r.productos < 0 or r.ahorro_y_deuda < 0:
                errores.append(f"[{user.username}] gasto negativo en {r.fecha}")

            # -------------------------------------------------------
            # 4) Gastos mayores al dinero disponible
            # -------------------------------------------------------
            if (r.alimento + r.productos + r.ahorro_y_deuda) > r.para_gastar_dia:
                errores.append(
                    f"[{user.username}] Gastos superan presupuesto en {r.fecha} → "
                    f"Gastado {r.alimento + r.productos + r.ahorro_y_deuda} / {r.para_gastar_dia}"
                )

            # -------------------------------------------------------
            # 5) Sobrante incoherente si no está fijo
            # -------------------------------------------------------
            if not r.sobrante_fijo:
                esperado = (
                    r.para_gastar_dia
                    - r.alimento
                    - r.productos
                    - r.ahorro_y_deuda
                )

                if r.sobrante_monetario != esperado:
                    errores.append(
                        f"[{user.username}] sobrante_monetario incorrecto en {r.fecha} → "
                        f"{r.sobrante_monetario} debería ser {esperado}"
                    )

            # -------------------------------------------------------
            # 6) Flags fijos inconsistentes
            # -------------------------------------------------------
            flags = [
                ("alimento_fijo", r.alimento),
                ("productos_fijo", r.productos),
                ("ahorro_y_deuda_fijo", r.ahorro_y_deuda),
                ("sobrante_fijo", r.sobrante_monetario),
            ]

            for flag, valor in flags:
                if getattr(r, flag) and valor < 0:
                    errores.append(
                        f"[{user.username}] {flag} activo pero valor negativo en {r.fecha}"
                    )

    # -------------------------------------------------------
    # 7) Resultado final
    # -------------------------------------------------------
    if errores:
        print("\n⚠️ ERRORES ENCONTRADOS:")
        for e in errores:
            print(" -", e)
    else:
        print("\n✅ No se encontraron registros corruptos.")

    print("\n=== Fin del análisis ===\n")
    return errores