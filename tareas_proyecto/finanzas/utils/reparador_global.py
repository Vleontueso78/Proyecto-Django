# finanzas/utils/reparador_global.py

from finanzas.utils.reparador import reparar_registros_financieros
from finanzas.models import User

def reparar_todos_los_usuarios():
    print("\n========================================")
    print(" Reparador Global — Todos los Usuarios ")
    print("========================================\n")

    resumen_global = {
        "usuarios_procesados": 0,
        "total_registros": 0,
        "fechas_fuera_de_rango": 0,
        "duplicados_eliminados": 0,
        "sobrantes_recalculados": 0,
        "decimales_corregidos": 0,
        "valores_negativos_corregidos": 0,
        "registros_actualizados": 0,
    }

    for user in User.objects.all():
        print(f"\n>>> Reparando registros del usuario: {user.username}")

        resultados = reparar_registros_financieros(user=user)

        # Acumular estadística por usuario
        resumen_global["usuarios_procesados"] += 1
        resumen_global["total_registros"] += resultados.get("total_registros", 0)
        resumen_global["fechas_fuera_de_rango"] += resultados["fechas_fuera_de_rango"]
        resumen_global["duplicados_eliminados"] += resultados["duplicados_eliminados"]
        resumen_global["sobrantes_recalculados"] += resultados["sobrantes_recalculados"]
        resumen_global["decimales_corregidos"] += resultados["decimales_corregidos"]
        resumen_global["valores_negativos_corregidos"] += resultados["valores_negativos_corregidos"]
        resumen_global["registros_actualizados"] += resultados["registros_actualizados"]

    print("\n========================================")
    print(" Reparación Global Finalizada ")
    print("========================================\n")

    print("Usuarios procesados:", resumen_global["usuarios_procesados"])
    print("Total de registros analizados:", resumen_global["total_registros"])
    print("Fechas fuera de rango:", resumen_global["fechas_fuera_de_rango"])
    print("Duplicados eliminados:", resumen_global["duplicados_eliminados"])
    print("Sobrantes recalculados:", resumen_global["sobrantes_recalculados"])
    print("Decimales corregidos:", resumen_global["decimales_corregidos"])
    print("Valores negativos corregidos:", resumen_global["valores_negativos_corregidos"])
    print("Registros actualizados:", resumen_global["registros_actualizados"])

    print("\n=== Fin del proceso global ===\n")

    return resumen_global