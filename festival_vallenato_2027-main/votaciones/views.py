from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.cache import add_never_cache_headers
from django.views.decorators.csrf import ensure_csrf_cookie
from .forms import CategoriaForm, EdicionForm, OpcionForm
from .models import Categoria, Edicion, Opcion, Votacion, Voto
from django.db.models import Count
from django.http import JsonResponse


# --- VISTA PÚBLICA DEL FESTIVAL (Solo Ediciones Activas) ---

def lista_votaciones(request):
    # Filtramos únicamente las ediciones activas ('1') y optimizamos con prefetch
    ediciones = Edicion.objects.filter(estado='1').prefetch_related('categorias__votaciones__opciones')
    
    # Conjunto para almacenar los IDs de las votaciones en las que el usuario ya votó
    votaciones_usuario_ids = set()
    if request.user.is_authenticated:
        votaciones_usuario_ids = set(
            Voto.objects.filter(usuario=request.user).values_list('votacion_id', flat=True)
        )
        
    return render(request, 'votaciones/lista_votaciones.html', {
        'ediciones': ediciones,
        'votaciones_usuario_ids': votaciones_usuario_ids
    })


# --- PANEL DE ADMINISTRACIÓN Y GESTIÓN ---

@login_required(login_url='/login/')
def crear_edicion(request):
    edicion_activa = Edicion.objects.filter(estado='1').first()
    ediciones_inactivas = Edicion.objects.filter(estado='0') # <- Obtenemos las ediciones desactivadas
    categorias = edicion_activa.categorias.all() if edicion_activa else []

    # Nos aseguramos de que cada categoría tenga su votación creada
    for cat in categorias:
        if not cat.votaciones.exists():
            Votacion.objects.create(
                categoria=cat, titulo=f'Votación - {cat.nombre}', activa=True
            )

    if request.method == 'POST':
        form = EdicionForm(request.POST)
        if form.is_valid():
            edicion = form.save()
            return redirect('crear_categoria', edicion_id=edicion.pk)
    else:
        form = EdicionForm()

    return render(
        request,
        'votaciones/crear_edicion.html',
        {
            'form': form, 
            'edicion_activa': edicion_activa, 
            'ediciones_inactivas': ediciones_inactivas, # <- Se las enviamos a la plantilla
            'categorias': categorias
        },
    )


@login_required(login_url='/login/')
def crear_categoria(request, edicion_id):
    edicion = get_object_or_404(Edicion, pk=edicion_id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.edicion = edicion
            categoria.save()

            Votacion.objects.create(
                categoria=categoria,
                titulo=f'Votación - {categoria.nombre}',
                activa=True,
            )

            return redirect('crear_edicion')
    else:
        form = CategoriaForm()

    return render(
        request,
        'votaciones/crear_categoria.html',
        {'form': form, 'edicion': edicion},
    )


@login_required(login_url='/login/')
@ensure_csrf_cookie
def crear_participante(request, votacion_id):
    votacion = get_object_or_404(Votacion, pk=votacion_id)

    if request.method == 'POST':
        form = OpcionForm(request.POST, request.FILES)
        if form.is_valid():
            opcion = form.save(commit=False)
            opcion.votacion = votacion

            if 'imagen_archivo' in request.FILES:
                imagen = request.FILES['imagen_archivo']
                file_path = default_storage.save(f'participantes/{imagen.name}', imagen)
                opcion.imagen_url = file_path
            else:
                opcion.imagen_url = ''

            opcion.save()
            return redirect('crear_edicion')
        else:
            print('Errores en formulario:', form.errors)
    else:
        form = OpcionForm()

    response = render(
        request, 'votaciones/crear_participante.html', {'form': form, 'votacion': votacion}
    )

    # Esto fuerza al navegador a pedir un token fresco y evita el error 403 por velocidad
    add_never_cache_headers(response)
    return response


@login_required(login_url='/login/')
def editar_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, pk=categoria_id)

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria)
        if form.is_valid():
            form.save()
            return redirect('crear_edicion')
    else:
        form = CategoriaForm(instance=categoria)

    return render(
        request,
        'votaciones/crear_categoria.html',
        {'form': form, 'edicion': categoria.edicion, 'categoria': categoria},
    )


@login_required(login_url='/login/')
def editar_participante(request, pk):
    participante = get_object_or_404(Opcion, pk=pk)

    if request.method == 'POST':
        form = OpcionForm(request.POST, request.FILES, instance=participante)
        if form.is_valid():
            opcion = form.save(commit=False)

            # Si el usuario subió una nueva foto, la procesamos y actualizamos la ruta
            if 'imagen_archivo' in request.FILES:
                imagen = request.FILES['imagen_archivo']
                file_path = default_storage.save(f'participantes/{imagen.name}', imagen)
                opcion.imagen_url = file_path

            opcion.save()
            return redirect('crear_edicion')
        else:
            print('Errores al editar participante:', form.errors)
    else:
        form = OpcionForm(instance=participante)

    return render(
        request,
        'votaciones/editar_participante.html',
        {'form': form, 'participante': participante},
    )


# --- SISTEMA DE VOTACIÓN PÚBLICA Y AUTENTICACIÓN DE VOTANTES ---

@login_required(login_url='/login/')
def emitir_voto(request, opcion_id):
    opcion = get_object_or_404(Opcion, pk=opcion_id)
    votacion = opcion.votacion

    # Validar estrictamente si el usuario ya emitió un voto en esta votación
    ya_voto = Voto.objects.filter(usuario=request.user, votacion=votacion).exists()

    if not ya_voto:
        Voto.objects.create(usuario=request.user, votacion=votacion, opcion=opcion)
        messages.success(request, "¡Tu voto ha sido registrado correctamente!")
    else:
        messages.warning(request, "Ya has emitido un voto en esta categoría.")

    return redirect('lista_votaciones')


def registro_votante(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Aseguramos que sea un usuario común sin permisos administrativos
            user.is_staff = False
            user.is_superuser = False
            user.save()
            messages.success(request, "¡Cuenta creada con éxito! Ya puedes iniciar sesión.")
            return redirect('login_votante')
    else:
        form = UserCreationForm()
    
    return render(request, 'votaciones/registro.html', {'form': form})


def login_votante(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            
            # Validación inteligente: Si es admin o staff, va al panel de creación/gestión
            if user.is_staff or user.is_superuser:
                return redirect('crear_edicion')
            else:
                # Si es un usuario común, va a la cartelera de votaciones pública
                return redirect('lista_votaciones')
    else:
        form = AuthenticationForm()
        
    return render(request, 'votaciones/login.html', {'form': form})


def cerrar_sesion_votante(request):
    logout(request)
    return redirect('lista_votaciones')


# --- MÓDULO DE RESULTADOS Y API GET PROTEGIDA ---

@login_required(login_url='/login/')
def ver_resultados_admin(request):
    ediciones = Edicion.objects.prefetch_related(
        'categorias__votaciones__opciones'
    )
    
    for edicion in ediciones:
        for categoria in edicion.categorias.all():
            for votacion in categoria.votaciones.all():
                for opcion in votacion.opciones.all():
                    opcion.conteo_votos = Voto.objects.filter(opcion=opcion).count()

    return render(request, 'votaciones/resultados_admin.html', {
        'ediciones': ediciones
    })


def api_lista_ediciones(request):
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({
            'status': 'error',
            'message': 'Acceso denegado. Se requieren permisos de administrador.'
        }, status=403)

    ediciones = list(Edicion.objects.values('id_edicion', 'nombre', 'anio', 'estado'))
    return JsonResponse({'status': 'success', 'ediciones': ediciones}, safe=False)

@login_required(login_url='/login/')
def desactivar_edicion(request, pk):
    edicion = get_object_or_404(Edicion, pk=pk)
    edicion.estado = '0'
    edicion.save()
    messages.success(request, f"La edición '{edicion.nombre}' ha sido desactivada correctamente.")
    return redirect('crear_edicion')

@login_required(login_url='/login/')
def activar_edicion(request, pk):
    edicion = get_object_or_404(Edicion, pk=pk)
    edicion.estado = '1'
    edicion.save()
    messages.success(request, f"La edición '{edicion.nombre}' ha sido activada correctamente.")
    return redirect('crear_edicion') 