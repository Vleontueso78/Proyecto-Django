from decimal import Decimal
from django.contrib.auth import get_user_model

from ..models import RegistroFinanciero, normalizar_decimal
from ..calculo_sobrante.calculadora import calcular_sobrante

User = get_user_model()


def verificar_registros_financieros():
    print("\n=== Verificador de Registros Financieros ===\n")

    total = RegistroFinanciero.objects.count()
    print(f"Total registros: {total}")

    errores = []
    usuarios = User.objects.all()

    for user in usuarios:
        registros = (
            RegistroFinanciero.objects
            .filter(user=user)
            .order_by("fecha")
        )

        # -------------------------------------------------------
        # 1) Fechas duplicadas por usuario
        # -------------------------------------------------------
        fechas_vistas = set()
        for r in registros:
            if r.fecha in fechas_vistas:
                errores.append(
                    f"[{user.username}] Duplicado en fecha {r.fecha}"
                )
            fechas_vistas.add(r.fecha)

        for r in registros:
            # -------------------------------------------------------
            # 2) Normalización segura de campos monetarios
            # -------------------------------------------------------
            campos = [
                "para_gastar_dia",
                "alimento",
                "productos",
                "ahorro_y_deuda",
                "sobrante_monetario",
            ]

            valores = {}
            for campo in campos:
                try:
                    valores[campo] = normalizar_decimal(getattr(r, campo))
                except Exception:
                    errores.append(
                        f"[{user.username}] {campo} contiene dato inválido → {getattr(r, campo)}"
                    )
                    valores[campo] = Decimal("0")

            # -------------------------------------------------------
            # 3) Valores negativos imposibles
            # -------------------------------------------------------
            if valores["para_gastar_dia"] < 0:
                errores.append(
                    f"[{user.username}] para_gastar_dia negativo en {r.fecha}"
                )

            if (
                valores["alimento"] < 0
                or valores["productos"] < 0
                or valores["ahorro_y_deuda"] < 0
            ):
                errores.append(
                    f"[{user.username}] gasto negativo en {r.fecha}"
                )

            # -------------------------------------------------------
            # 4) Gastos mayores al dinero disponible
            # -------------------------------------------------------
            total_gastos = (
                valores["alimento"]
                + valores["productos"]
                + valores["ahorro_y_deuda"]
            )

            if total_gastos > valores["para_gastar_dia"]:
                errores.append(
                    f"[{user.username}] Gastos superan presupuesto en {r.fecha} → "
                    f"Gastado {total_gastos} / {valores['para_gastar_dia']}"
                )

            # -------------------------------------------------------
            # 5) Sobrante incoherente si no está fijo
            # -------------------------------------------------------
            if not r.sobrante_fijo:
                esperado = normalizar_decimal(
                    calcular_sobrante(
                        valores["para_gastar_dia"],
                        valores["alimento"],
                        valores["ahorro_y_deuda"],
                        valores["productos"],
                    )
                )

                if valores["sobrante_monetario"] != esperado:
                    errores.append(
                        f"[{user.username}] sobrante_monetario incorrecto en {r.fecha} → "
                        f"{valores['sobrante_monetario']} debería ser {esperado}"
                    )

            # -------------------------------------------------------
            # 6) Flags fijos inconsistentes
            # -------------------------------------------------------
            flags = [
                ("alimento_fijo", valores["alimento"]),
                ("productos_fijo", valores["productos"]),
                ("ahorro_y_deuda_fijo", valores["ahorro_y_deuda"]),
                ("sobrante_fijo", valores["sobrante_monetario"]),
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