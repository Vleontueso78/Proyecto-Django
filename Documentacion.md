# 🧩 Proyecto: Organizador Personal

Aplicación web desarrollada con **Django**, pensada como un organizador personal integral que permite a los usuarios gestionar sus **tareas, notas y finanzas** de manera simple y eficiente.  
Incluye **autenticación segura con Google OAuth2**, una **interfaz moderna** y **paneles visuales** para controlar y planificar la información diaria desde un mismo lugar.

---

## 📂 Estructura del Proyecto

```
tareas_proyecto/
│
├── tareas_proyecto/              # Configuración principal de Django
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   ├── asgi.py
│
├── finanzas/                     # App para control financiero
│   ├── migrations/
│   ├── templates/finanzas/
│   │   ├── dashboard.html
│   │   ├── registros.html
│   │   ├── crear_objetivo.html
│   ├── static/finanzas/css/
│   │   ├── finanzas_dashboard.css
│   │   ├── finanzas_registros.css
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│
├── tareas/                       # App de gestión de tareas
│   ├── migrations/
│   ├── templates/tareas/
│   │   ├── crear.html
│   │   ├── editar.html
│   │   ├── lista.html
│   │   ├── dashboard.html
│   │   ├── base.html
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   ├── static/tareas/css/
│
├── tareasMauri/                  # App para gestión de notas
│   ├── templates/tareasMauri/
│   │   ├── inicio.html
│   │   ├── notas.html
│   │   ├── crear_notas.html
│   │   ├── editar_nota.html
│   ├── models.py
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│
├── usuarios/                     # App para autenticación y login
│   ├── templates/usuarios/
│   │   ├── login.html
│   │   ├── registro.html
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│
├── static/                       # Archivos CSS y JS compartidos
│   ├── css/
│   ├── js/
│
├── db.sqlite3                    # Base de datos local (no se sube al repo)
├── manage.py
├── requirements.txt              # Dependencias del proyecto
└── README.md
```

---

## 🚀 Instalación y Ejecución Local

Sigue estos pasos para levantar el proyecto en tu entorno local 👇

---

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

## 🔐 4️⃣ Crear y configurar el archivo `.env`

``` env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost

EMAIL_HOST=smtp.example.com
EMAIL_USER=tu_email@example.com
EMAIL_PASSWORD=tu_contraseña
EMAIL_PORT=587
EMAIL_USE_TLS=True

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=your-google-client-id
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=your-google-client-secret
```

---

### 4️⃣ 🔐 Configurar inicio de sesión con Google OAuth2

1. Accedé a [Google Cloud Console](https://console.cloud.google.com/).
2. Creá un **nuevo proyecto**.
3. En **APIs y servicios → Credenciales**, generá un **ID de cliente OAuth2**.
4. Configurá los siguientes valores:
   - **Origen autorizado:** `http://127.0.0.1:8000`
   - **URI de redirección:** `http://127.0.0.1:8000/accounts/google/login/callback/`
5. Copiá el `Client ID` y el `Client Secret` y agregalos a tu archivo `.env`:

   ```env
   SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=TU_CLIENT_ID
   SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=TU_CLIENT_SECRET
   ```

---

### 5️⃣ Crear la base de datos local

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 6️⃣ Crear un superusuario

```bash
python manage.py createsuperuser
```

---

### 7️⃣ Ejecutar el servidor

```bash
python manage.py runserver
```

👉 Luego abrí tu navegador en:  
[http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## ⚙️ Aplicaciones del Proyecto

| Aplicación      | Descripción |
|-----------------|-------------|
| `tareas`        | Permite crear, editar y organizar tareas personales. |
| `tareasMauri`   | Sistema de notas personales y recordatorios. |
| `finanzas`      | Registro de gastos, ingresos y objetivos financieros. |
| `usuarios`      | Autenticación, login y registro (con soporte para Google OAuth2). |

---

## 🧠 Tecnologías Utilizadas

- **Python 3**
- **Django 5**
- **SQLite3**
- **Google OAuth2**
- **HTML / CSS / Bootstrap 5**

---

## 💡 Autor

👤 **Raúl T.**  
Desarrollado como parte del **proyecto final de la diplomatura en desarrollo web**.  
📬 GitHub: [raultueso2006](https://github.com/raultueso2006)
