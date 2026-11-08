from django.conf import settings
from django.db import models

class Edicion(models.Model):
    id_edicion = models.AutoField(primary_key=True, db_column='id')
    nombre = models.CharField(max_length=100)
    anio = models.SmallIntegerField(db_index=True)
    estado = models.CharField(max_length=20, default='1')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'votaciones_edicion'

    def __str__(self):
        return f"{self.nombre} ({self.anio})"


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True, db_column='id')
    edicion = models.ForeignKey(Edicion, on_delete=models.CASCADE, db_column='edicion_id', related_name='categorias')
    nombre = models.CharField(max_length=120)
    subtitulo = models.CharField(max_length=150, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'votaciones_categoria'

    def __str__(self):
        return f"{self.nombre} - {self.edicion.nombre}"


class Votacion(models.Model):
    id_votacion = models.AutoField(primary_key=True, db_column='id')
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, db_column='categoria_id', related_name='votaciones')
    titulo = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    activa = models.BooleanField(default=True)
    fecha_cierre = models.DateTimeField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'votaciones_votacion'

    def __str__(self):
        return self.titulo


class Opcion(models.Model):
    id_opcion = models.AutoField(primary_key=True, db_column='id')
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, db_column='votacion_id', related_name='opciones')
    nombre = models.CharField(max_length=160)
    subtitulo = models.CharField(max_length=150, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    imagen_url = models.CharField(max_length=255, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'votaciones_opcion'

    def __str__(self):
        return self.nombre


class Voto(models.Model):
    id_voto = models.AutoField(primary_key=True, db_column='id')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, db_column='usuario_id')
    votacion = models.ForeignKey(Votacion, on_delete=models.CASCADE, db_column='votacion_id')
    opcion = models.ForeignKey(Opcion, on_delete=models.CASCADE, db_column='opcion_id', related_name='votos')
    codigo_transaccion = models.CharField(max_length=36, db_index=True, unique=True, blank=True, null=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votaciones_voto'
        unique_together = ('usuario', 'votacion')

    def __str__(self):
        return f"Voto de {self.usuario.username} por {self.opcion.nombre}"


class AuditoriaLog(models.Model):
    id_log = models.AutoField(primary_key=True, db_column='id')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='usuario_id')
    accion = models.CharField(max_length=255)
    detalles = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votaciones_auditoria_log'

    def __str__(self):
        return f"[{self.fecha_creacion}] {self.usuario}: {self.accion}"

class AuditoriaEliminacion(models.Model):
    id_eliminacion = models.AutoField(primary_key=True, db_column='id')
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, db_column='usuario_id')
    tipo_objeto = models.CharField(max_length=50) # Ejemplo: "Categoría" o "Participante"
    objeto_nombre = models.CharField(max_length=160)
    detalles = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'votaciones_auditoria_eliminacion'

    def __str__(self):
        return f"Eliminación de {self.tipo_objeto}: {self.objeto_nombre}"