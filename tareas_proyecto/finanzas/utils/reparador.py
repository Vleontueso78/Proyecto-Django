# finanzas/utils/reparador.py

from decimal import Decimal
from django.db import connection

from ..models import (
    RegistroFinanciero,
    ConfigFinanciera,
    normalizar_decimal,
)
from ..calculo_sobrante.calculadora import calcular_sobrante


# -----------------------------------------------------
# Reparador completo de registros financieros
# -----------------------------------------------------
def reparar_registros_financieros(usuario=None, verbose=False):
    if verbose:
        print("\n=== Reparador Automático de Registros ===\n")

    registros = RegistroFinanciero.objects.all()
    if usuario:
        registros = registros.filter(user=usuario)

    total = registros.count()
    if verbose:
        print(f"Total registros a analizar: {total}\n")

    arreglados = {
        "fechas_fuera_de_rango": 0,
        "duplicados_eliminados": 0,
        "sobrantes_recalculados": 0,
        "decimales_corregidos": 0,
        "valores_negativos_corregidos": 0,
        "registros_actualizados": 0,
    }

    # --------------------------------------------
    # 1) Arreglar fechas fuera del rango permitido
    #    (blindado contra ConfigFinanciera corrupta)
    # --------------------------------------------
    for reg in registros:
        try:
            config = (
                ConfigFinanciera.objects
                .only("fecha_inicio_registros")
                .get(user=reg.user)
            )

            f_inicio = config.fecha_inicio_registros

            if f_inicio and reg.fecha < f_inicio:
                if verbose:
                    print(f"⚠ Fecha fuera de rango → {reg.fecha} < {f_inicio}")
                reg.fecha = f_inicio
                reg.save(update_fields=["fecha"])
                arreglados["fechas_fuera_de_rango"] += 1

        except Exception as e:
            if verbose:
                print(
                    f"⚠ ConfigFinanciera inválida para usuario {reg.user} "
                    f"(se omite ajuste de fecha): {e}"
                )

    # --------------------------------------------
    # 2) Eliminar duplicados manteniendo el mejor
    # --------------------------------------------
    vistos = {}

    for reg in registros.order_by("fecha"):
        key = (reg.user_id, reg.fecha)

        if key not in vistos:
            vistos[key] = reg
            continue

        reg_original = vistos[key]

        campos = ["alimento", "productos", "ahorro_y_deuda", "para_gastar_dia"]

        suma_original = sum(
            normalizar_decimal(getattr(reg_original, c)) for c in campos
        )
        suma_nuevo = sum(
            normalizar_decimal(getattr(reg, c)) for c in campos
        )

        if suma_nuevo > suma_original:
            if verbose:
                print(f"🔄 Reemplazando registro por uno más completo en {reg.fecha}")
            reg_original.delete()
            vistos[key] = reg
        else:
            if verbose:
                print(f"🗑 Eliminando duplicado inferior en {reg.fecha}")
            reg.delete()

        arreglados["duplicados_eliminados"] += 1

    # --------------------------------------------
    # 3) Revisar y normalizar cada registro
    # --------------------------------------------
    for reg in registros:
        modificado = False

        # --- Normalizar campos monetarios ---
        for campo in ["alimento", "productos", "ahorro_y_deuda", "para_gastar_dia"]:
            valor_normalizado = normalizar_decimal(getattr(reg, campo))

            if getattr(reg, campo) != valor_normalizado:
                setattr(reg, campo, valor_normalizado)
                modificado = True
                arreglados["decimales_corregidos"] += 1

            if valor_normalizado < 0:
                setattr(reg, campo, Decimal("0"))
                modificado = True
                arreglados["valores_negativos_corregidos"] += 1

        # --- Recalcular sobrante (solo si no es fijo) ---
        if not reg.sobrante_fijo:
            sobrante_calculado = normalizar_decimal(
                calcular_sobrante(
                    reg.para_gastar_dia,
                    reg.alimento,
                    reg.ahorro_y_deuda,
                    reg.productos,
                )
            )

            if reg.sobrante_monetario != sobrante_calculado:
                if verbose:
                    print(f"♻ Recalculando sobrante en {reg.fecha}")
                reg.sobrante_monetario = sobrante_calculado
                modificado = True
                arreglados["sobrantes_recalculados"] += 1

        if modificado:
            reg.save()
            arreglados["registros_actualizados"] += 1

    if verbose:
        print("\n=== Reparación Completada ===\n")
        for k, v in arreglados.items():
            print(f"{k}: {v}")
        print("\n=== Fin del proceso ===\n")

    return arreglados


# -----------------------------------------------------
# Reparador SQL seguro para ConfigFinanciera
# -----------------------------------------------------
def reparar_config_financiera_sql(verbose=False):
    """
    Reparación SQL completa de ConfigFinanciera.
    Normaliza cualquier valor inválido sin usar ORM.
    """

    campos_decimales = [
        "presupuesto_diario",
        "default_alimento",
        "default_productos",
        "default_ahorro_y_deuda",
        "default_sobrante",
    ]

    with connection.cursor() as cursor:
        for campo in campos_decimales:
            cursor.execute(f"""
                UPDATE finanzas_configfinanciera
                SET {campo} = 0
                WHERE {campo} IS NULL
                   OR TRIM({campo}) = ''
                   OR {campo} = 'NaN'
                   OR {campo} = 'None'
                   OR {campo} = '-'
                   OR {campo} = '--'
            """)

            if verbose:
                print(f"✔ Campo reparado (forzado): {campo}")