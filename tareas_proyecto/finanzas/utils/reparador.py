from decimal import Decimal, InvalidOperation
from datetime import date

from ..models import RegistroFinanciero, ConfigFinanciera
from ..calculo_sobrante.calculadora import calcular_sobrante


# -----------------------------------------------------
# Conversión segura a Decimal
# -----------------------------------------------------
def safe_decimal(value, default=Decimal("0")):
    try:
        if value in [None, "", " ", "-", "--"]:
            return default
        return Decimal(str(value).replace(",", "."))
    except (InvalidOperation, TypeError, ValueError):
        return default


# -----------------------------------------------------
# Reparador completo de registros
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
    # --------------------------------------------
    for reg in registros:
        try:
            config = ConfigFinanciera.objects.get(user=reg.user)
            f_inicio = config.fecha_inicio_registros

            if f_inicio and reg.fecha < f_inicio:
                if verbose:
                    print(f"⚠ Fecha fuera de rango → {reg.fecha} < {f_inicio}")
                reg.fecha = f_inicio
                reg.save()
                arreglados["fechas_fuera_de_rango"] += 1
        except ConfigFinanciera.DoesNotExist:
            pass

    # --------------------------------------------
    # 2) Eliminar duplicados manteniendo el mejor registro
    # --------------------------------------------
    vistos = {}

    for reg in registros.order_by("fecha"):
        key = (reg.user.id, reg.fecha)

        if key not in vistos:
            vistos[key] = reg
        else:
            reg_original = vistos[key]

            campos = ["alimento", "productos", "ahorro_y_deuda", "para_gastar_dia"]
            suma_original = sum([getattr(reg_original, c) for c in campos])
            suma_nuevo = sum([getattr(reg, c) for c in campos])

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
    # 3) Revisar cada registro individual
    # --------------------------------------------
    for reg in RegistroFinanciero.objects.all():

        modificado = False

        # --- Normalizar decimales ---
        for campo in ["alimento", "productos", "ahorro_y_deuda", "para_gastar_dia"]:
            valor = getattr(reg, campo)
            valor_dec = safe_decimal(valor)

            if valor_dec != valor:
                setattr(reg, campo, valor_dec)
                modificado = True
                arreglados["decimales_corregidos"] += 1

            # Corregir valores negativos
            if valor_dec < 0:
                setattr(reg, campo, Decimal("0"))
                modificado = True
                arreglados["valores_negativos_corregidos"] += 1

        # --- Recalcular sobrante ---
        sobrante_calculado = calcular_sobrante(
            reg.para_gastar_dia,
            reg.alimento,
            reg.ahorro_y_deuda,
            reg.productos
        )

        if not reg.sobrante_fijo:
            if reg.sobrante_monetario != sobrante_calculado:
                if verbose:
                    print(f"♻ Recalculando sobrante en {reg.fecha}")
                reg.sobrante_monetario = sobrante_calculado
                modificado = True
                arreglados["sobrantes_recalculados"] += 1

        # Guardar cambios
        if modificado:
            reg.save()
            arreglados["registros_actualizados"] += 1

    if verbose:
        print("\n=== Reparación Completada ===\n")
        for k, v in arreglados.items():
            print(f"{k}: {v}")
        print("\n=== Fin del proceso ===\n")

    return arreglados