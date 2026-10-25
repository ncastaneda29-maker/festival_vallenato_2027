from django.db import models

class Edicion(models.Model):
    nombre = models.CharField(max_length=100)
    anio = models.IntegerField()
    estado = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Edición"
        verbose_name_plural = "Ediciones"

    def __str__(self):
        return f"{self.nombre} ({self.anio})"


class Categoria(models.Model):
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, related_name='categorias')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

    def __str__(self):
        return f"{self.nombre} - {self.edicion.nombre}"


class Votacion(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='votaciones')
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Votación"
        verbose_name_plural = "Votaciones"

    def __str__(self):
        return f"{self.titulo} ({self.categoria.nombre})"


class Opcion(models.Model):
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, related_name='opciones')
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    imagen_url = models.URLField(blank=True, null=True)

    class Meta:
        verbose_name = "Opción"
        verbose_name_plural = "Opciones"

    def __str__(self):
        return f"{self.nombre} - {self.votacion.titulo}"