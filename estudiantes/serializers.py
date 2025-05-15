from rest_framework import serializers
from .models import Estudiante, Respuesta, RespuestaFinal, TiempoRA

class EstudianteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Estudiante
        fields = ['id', 'nombres', 'apellidos', 'edad', 'grado', 'salon']

class RespuestaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Respuesta
        fields = '__all__'

class RespuestaFinalSerializer(serializers.ModelSerializer):
    class Meta:
        model = RespuestaFinal
        fields = '__all__'

class TiempoRASerializer(serializers.ModelSerializer):
    class Meta:
        model = TiempoRA
        fields = '__all__'
