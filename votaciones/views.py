from django.shortcuts import render
from .models import Edicion

def lista_votaciones(request):
    ediciones = Edicion.objects.filter(estado=True)
    return render(request, 'votaciones/lista_votaciones.html', {'ediciones': ediciones})