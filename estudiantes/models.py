from django.db import models
from django.utils import timezone

class Estudiante(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    edad = models.IntegerField()
    grado = models.CharField(max_length=100)
    salon = models.CharField(max_length=100)

    def __str__(self):
        return str(self.nombres)

class Respuesta(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=255)  
    opcion_elegida = models.CharField(max_length=255)  

class RespuestaFinal(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    pregunta = models.CharField(max_length=255)  
    opcion_elegida = models.CharField(max_length=255)  

class TiempoRA(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    hora_inicio = models.DateTimeField()
    hora_fin = models.DateTimeField(null=True, blank=True)
    duracion = models.DurationField(null=True, blank=True)
    fecha = models.DateField(default=timezone.now)

    def save(self, *args, **kwargs):
        # Si ya hay hora_inicio y hora_fin, calcula la duración
        if self.hora_inicio and self.hora_fin:
            self.duracion = self.hora_fin - self.hora_inicio
        super().save(*args, **kwargs)