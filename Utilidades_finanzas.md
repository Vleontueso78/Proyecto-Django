# Documentación de Comandos y Utilidades de Finanzas

## 🎯 Objetivo de esta Documentación

Este documento sirve como guía rápida para entender y ejecutar todos los
comandos internos del módulo **Finanzas** del proyecto Django.\
Incluye una explicación clara del propósito de cada archivo, cómo
ejecutarlo y para qué sirve cada comando.

También se detalla el uso de `exit()` al trabajar dentro del entorno
interactivo de Django.

------------------------------------------------------------------------

## 🔚 Comando `exit()`

**Uso:**

    exit()

**¿Para qué sirve?**\
Se utiliza dentro de la consola interactiva de Python o del shell de
Django para **cerrar la sesión y volver a la terminal**.\
Es útil cuando finalizaste pruebas dentro del shell.

------------------------------------------------------------------------

# 📂 Archivos Documentados

A continuación se explican todos los archivos solicitados:

------------------------------------------------------------------------

# 1. `reparar_finanzas.py`

**Ubicación:**\
`tareas_proyecto/finanzas/management/commands/reparar_finanzas.py`

### 📌 ¿Qué es?

Es un **comando de Django** ejecutable desde la consola para
diagnosticar y reparar automáticamente los registros financieros de
todos los usuarios.

### ▶️ ¿Cómo se ejecuta?

    python manage.py reparar_finanzas

### 🔧 Opciones disponibles:

  Opción        Descripción
  ------------- --------------------------------------
  `--reparar`   Aplica reparaciones automáticamente
  `--verbose`   Muestra detalle completo del proceso

### 🧪 Ejemplo:

    python manage.py reparar_finanzas --reparar --verbose

------------------------------------------------------------------------

# 2. `diagnostico.py`

**Ubicación:**\
`tareas_proyecto/finanzas/utils/diagnostico.py`

### 📌 ¿Qué es?

Contiene funciones que **analizan los registros financieros** buscando
errores comunes: - Fechas inválidas\
- Valores negativos\
- Campos corruptos\
- Decimales incorrectos

### ▶️ ¿Cómo se ejecuta?\*\*

Desde el shell de Django:

    python manage.py shell

Dentro del shell:

``` python
from finanzas.utils.diagnostico import diagnosticar_registros
diagnosticar_registros(usuario=None)  # Para todos los usuarios
```

------------------------------------------------------------------------

# 3. `reparador_global.py`

**Ubicación:**\
`tareas_proyecto/finanzas/utils/reparador_global.py`

### 📌 ¿Qué es?

Script encargado de **reparar todos los registros de todos los
usuarios**, pensado para automatizaciones:

-   Cron jobs\
-   Tareas programadas\
-   Scripts externos

### ▶️ ¿Cómo se ejecuta dentro del shell?

    python manage.py shell

``` python
from finanzas.utils.reparador_global import reparar_todo
reparar_todo()
```

------------------------------------------------------------------------

# 4. `reparador.py`

**Ubicación:**\
`tareas_proyecto/finanzas/utils/reparador.py`

### 📌 ¿Qué es?

El reparador principal a nivel unitario.\
Se encarga de:

-   Arreglar fechas fuera de rango\
-   Normalizar decimales\
-   Corregir valores negativos\
-   Recalcular sobrantes\
-   Eliminar duplicados\
-   Regenerar datos corruptos

### ▶️ ¿Cómo se usa desde el shell?

    python manage.py shell

``` python
from finanzas.utils.reparador import reparar_registros_financieros
reparar_registros_financieros()
```

------------------------------------------------------------------------

# 5. `verificador.py`

**Ubicación:**\
`tareas_proyecto/finanzas/utils/verificador.py`

### 📌 ¿Qué es?

Un módulo ligero que **verifica si un conjunto de registros está sano o
corrupto**.\
Es útil antes de ejecutar reparaciones.

### ▶️ Ejecución desde el shell:

    python manage.py shell

``` python
from finanzas.utils.verificador import verificar_registros
verificar_registros()
```

------------------------------------------------------------------------

# ✔️ Conclusión

Con esta documentación podrás recordar fácilmente:

-   Qué hace cada archivo\
-   Cómo se ejecutan\
-   Para qué sirven los comandos\
-   Cómo reparar o diagnosticar la base de datos de finanzas

Ideal para mantenimiento, soporte y evolución del proyecto.

------------------------------------------------------------------------
