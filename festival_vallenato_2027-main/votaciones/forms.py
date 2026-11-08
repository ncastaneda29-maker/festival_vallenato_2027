from django import forms
from .models import Edicion, Categoria, Votacion, Opcion

class EdicionForm(forms.ModelForm):
    ESTADOS_CHOICES = [
        (1, 'Activa'),
        (0, 'Inactiva'),
    ]
    
    estado = forms.ChoiceField(
        choices=ESTADOS_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select',
            'style': 'color: #000000 !important; background-color: #ffffff !important;'
        }),
        label='Estado de la Edición'
    )

    class Meta:
        model = Edicion
        fields = ['nombre', 'anio', 'estado']
        labels = {
            'nombre': 'Nombre de la Edición',
            'anio': 'Año del Festival',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'style': 'color: #000000 !important; background-color: #ffffff !important;', 
                'placeholder': 'Ej. Festival Vallenato 2027'
            }),
            'anio': forms.NumberInput(attrs={
                'class': 'form-control', 
                'style': 'color: #000000 !important; background-color: #ffffff !important;', 
                'placeholder': 'Ej. 2027',
                'min': '2020',
                'max': '2030'
            }),
        }


class CategoriaForm(forms.ModelForm):
    class Meta:
        model = Categoria
        fields = ['nombre', 'descripcion']
        labels = {
            'nombre': 'Nombre de la Categoría',
            'descripcion': 'Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control', 
                'style': 'color: #000000 !important; background-color: #ffffff !important;', 
                'placeholder': 'Ej. Acordeonero Profesional'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control', 
                'style': 'color: #000000 !important; background-color: #ffffff !important;', 
                'rows': 3,
                'placeholder': 'Detalles de la categoría...'
            }),
        }


class OpcionForm(forms.ModelForm):
    imagen_archivo = forms.ImageField(
        required=False,
        label='Foto del Participante',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'style': 'color: #000000 !important; background-color: #ffffff !important;'
        })
    )
    
    # Declaramos imagen_url explícitamente como campo con required=False y HiddenInput
    imagen_url = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = Opcion
        fields = ['nombre', 'descripcion', 'imagen_url']
        labels = {
            'nombre': 'Nombre del Participante',
            'descripcion': 'Reseña o Descripción',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'style': 'color: #000000 !important; background-color: #ffffff !important;',
                'placeholder': 'Ej. Juan Pérez / Agrupación Vallenata'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-control',
                'style': 'color: #000000 !important; background-color: #ffffff !important;',
                'rows': 3,
                'placeholder': 'Breve información del concursante...'
            }),
        }