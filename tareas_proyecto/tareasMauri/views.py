from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Nota
from .forms import NotaForm

def inicio(request):
    """Página de inicio pública. Si el usuario está autenticado, lo redirige al menú principal."""
    if request.user.is_authenticated:
        return redirect('tareas:dashboard')
    return render(request, "tareasMauri/inicio.html")


@login_required
def lista_notas(request):
    notes = Nota.objects.filter(user=request.user).order_by('-created_at')
    return render(request, "tareasMauri/notas.html", {
        "notes": notes,
        "active": "notas"
    })


@login_required
def crear_nota(request):
    if request.method == 'POST':
        form = NotaForm(request.POST)
        if form.is_valid():
            nota = form.save(commit=False)
            nota.user = request.user
            nota.save()
            return redirect('tareasMauri:notas')
    else:
        form = NotaForm()
    return render(request, "tareasMauri/crear_notas.html", {
        "form": form,
        "active": "notas"
    })


@login_required
def editar_nota(request, id):
    nota = get_object_or_404(Nota, id=id, user=request.user)
    if request.method == 'POST':
        form = NotaForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            return redirect('tareasMauri:notas')
    else:
        form = NotaForm(instance=nota)
    return render(request, "tareasMauri/editar_nota.html", {
        "form": form,
        "nota": nota,
        "active": "notas"
    })


@login_required
def eliminar_nota(request, id):
    nota = get_object_or_404(Nota, id=id, user=request.user)
    nota.delete()
    return redirect('tareasMauri:notas')