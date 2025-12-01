from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView
from tareasMauri import views as mauri_views
from django.urls import reverse_lazy

urlpatterns = [
    path('admin/', admin.site.urls),

    # Página de inicio pública
    path('', mauri_views.inicio, name='inicio'),

    # Menú principal (redirige al dashboard de tareas)
    path('menu/', RedirectView.as_view(url=reverse_lazy('tareas:dashboard')), name='menu'),

    # Apps del proyecto
    path('tareas/', include(('tareas.urls', 'tareas'), namespace='tareas')),
    path('mauri/', include(('tareasMauri.urls', 'tareasMauri'), namespace='tareasMauri')),
    path('usuarios/', include('usuarios.urls')),

    # namespace
    path('finanzas/', include(('finanzas.urls', 'finanzas'), namespace='finanzas')),

    # Login / Logout
    path(
        'accounts/login/',
        auth_views.LoginView.as_view(template_name='registration/login.html'),
        name='login'
    ),
    path(
        'accounts/logout/',
        auth_views.LogoutView.as_view(next_page=reverse_lazy('inicio')),
        name='logout'
    ),

    # Login con Google
    path('oauth/', include('social_django.urls', namespace='social')),
]