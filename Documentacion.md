# 🧩 Proyecto: Organizador personal

Aplicación web desarrollada con Django, pensada como un organizador personal integral que permite a los usuarios gestionar sus tareas, notas y finanzas de manera simple y eficiente.
Incluye autenticación segura con Google OAuth2, una interfaz moderna y paneles visuales para controlar y planificar la información diaria desde un mismo lugar.

---

## 📂 Estructura del Proyecto

```
tareas_proyecto/
│
├── tareas_proyecto/ # Configuración principal de Django
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
│ ├── asgi.py
│
├── finanzas/ # App para control financiero
│ ├── migrations/
│ ├── templates/finanzas/
│ │ ├── dashboard.html
│ │ ├── registros.html
│ │ ├── objetivo_financiero.py
│ ├── static/finanzas/css/
│ │ ├── finanzas_dashboard.css
│ │ ├── finanzas_registros.css
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│ ├── forms.py
│ ├── admin.py
│
├── tareas/ # App de gestión de tareas
│ ├── migrations/
│ ├── templates/tareas/
│ │ ├── crear.html
│ │ ├── editar.html
│ │ ├── lista.html
│ │ ├── dashboard.html
│ │ ├── base.html
│ ├── models.py
│ ├── forms.py
│ ├── views.py
│ ├── urls.py
│ ├── static/tareas/css/
│
├── tareasMauri/ # App extra con gestión de notas
│ ├── templates/tareasMauri/
│ │ ├── inicio.html
│ │ ├── notas.html
│ │ ├── crear_notas.html
│ │ ├── editar_nota.html
│ ├── models.py
│ ├── forms.py
│ ├── views.py
│ ├── urls.py
│
├── usuarios/ # App para manejo de usuarios y login
│ ├── templates/usuarios/
│ │ ├── login.html
│ │ ├── registro.html
│ ├── models.py
│ ├── views.py
│ ├── urls.py
│
├── static/ # Archivos CSS y JS compartidos
│ ├── css/
│ ├── js/
│
├── db.sqlite3 # Base de datos local (no se sube al repo)
├── manage.py
├── requirements.txt # Dependencias del proyecto
└── Documentacion.md
```

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para levantar el proyecto en tu entorno local 👇

### 1️⃣ Clonar el repositorio

```bash
git clone https://github.com/Vleontueso78/Proyecto-Django.git
cd Proyecto-Django
```

---

### 2️⃣ Crear y activar el entorno virtual

#### 🪟 En Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

#### 🐧 En Linux / Mac:
```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3️⃣ Instalar dependencias

```bash
pip install -r requirements.txt
```

---

### 4️⃣ Crear la base de datos local 🗃️

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5️⃣ Crear un superusuario (opcional por si queres administrar la base de datos)

```bash
python manage.py createsuperuser
```

---

### 6 🔐 Configuración de Inicio de Sesión con Google OAuth2

Para usar el **login con Google**, seguí estos pasos:

1. Ingresá a [Google Cloud Console](https://console.cloud.google.com/).
2. Creá un **nuevo proyecto** (o seleccioná uno existente).
3. En el menú lateral, entrá a **APIs y servicios → Credenciales**.
4. Hacé clic en **Crear credenciales → ID de cliente de OAuth**.
5. Configurá la pantalla de consentimiento con:
   - Nombre de la app: *Organizador personal*
   - Correo del desarrollador
6. En **Tipo de aplicación**, elegí **Aplicación web**.
7. En **Orígenes autorizados de JavaScript**, agregá:
   ```
   http://127.0.0.1:8000
   ```
8. En **URIs de redirección autorizados**, agregá:
   ```
   http://127.0.0.1:8000/accounts/google/login/callback/
   ```
9. Google te dará:
   - **Client ID**
   - **Client Secret**

10. En tu archivo `.env` (o directamente en `settings.py` si aún no usás variables de entorno), agregá:

    ```python
    SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = 'TU_CLIENT_ID'
    SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = 'TU_CLIENT_SECRET'
    ```

11. Reiniciá el servidor y verificá el botón de inicio de sesión con Google en `/login/`.

### 7 Ejecutar el servidor

```bash
python manage.py runserver
```

👉 Abrí tu navegador en:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---



---

## ⚙️ Aplicaciones del Proyecto

| Aplicación     | Descripción |
|----------------|-------------|
| `catalogo`     | Gestión de libros, películas y series. |
| `recomendador` | Muestra recomendaciones personalizadas y el panel principal. |
| `usuarios`     | Maneja el registro, login tradicional y login con Google. |

---

## 🧠 Tecnologías Utilizadas

- **Python 3**
- **Django 5**
- **SQLite3**
- **OAuth2 (Google)**
- **HTML / CSS**
- **Bootstrap 5**

---

## 📜 Notas Importantes

- Activá siempre tu entorno virtual antes de ejecutar el proyecto.
- La base de datos `db.sqlite3` no se sube al repositorio; se genera con las migraciones.
- Si agregás nuevas dependencias, actualizá el archivo `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```

---

## 💡 Autor

👤 **Raúl T.**  
Desarrollado como parte del proyecto final de diplomatura en desarrollo web.  
📬 GitHub: [raultueso2006](https://github.com/raultueso2006)
