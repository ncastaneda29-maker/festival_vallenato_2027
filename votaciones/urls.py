from django.urls import path
from . import views

urlpatterns = [
    path('', views.lista_votaciones, name='lista_votaciones'),
]