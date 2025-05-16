from rest_framework import generics
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework import status
from .models import Estudiante, Respuesta, RespuestaFinal, TiempoRA
from .serializers import EstudianteSerializer, RespuestaSerializer, RespuestaFinalSerializer, TiempoRASerializer
from rest_framework.views import APIView
from datetime import datetime, timezone

class EstudianteListCreate(generics.ListCreateAPIView):
    queryset = Estudiante.objects.all()  # pylint: disable=no-member
    serializer_class = EstudianteSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            estudiante = serializer.save()  # Guarda el estudiante en la BD
            return Response(
                {"mensaje": "Estudiante registrado", "id": estudiante.id},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RespuestaCreate(generics.ListAPIView):
    serializer_class = RespuestaSerializer

    def get_queryset(self):
        estudiante_id = self.request.query_params.get('estudiante_id', None)
        if estudiante_id is not None:
            return Respuesta.objects.filter(estudiante_id=estudiante_id) # pylint: disable=no-member
        return Respuesta.objects.all() # pylint: disable=no-member

    def post(self, request, *args, **kwargs):
        estudiante_id = request.data.get('estudiante')
        pregunta = request.data.get('pregunta')
        opcion_elegida = request.data.get('opcion_elegida')

        if not estudiante_id or not pregunta or not opcion_elegida:
            return Response({"error": "Faltan datos necesarios"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la nueva respuesta
        respuesta = Respuesta.objects.create( # pylint: disable=no-member
            estudiante_id=estudiante_id,
            pregunta=pregunta,
            opcion_elegida=opcion_elegida
        )

        # Serializar la respuesta creada
        serializer = RespuestaSerializer(respuesta)

        # Devolver la respuesta creada en la respuesta HTTP
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RespuestasPorEstudiante(APIView):
    def get(self, request, estudiante_id):
        respuestas = Respuesta.objects.filter(estudiante_id=estudiante_id) # pylint: disable=no-member
        serializer = RespuestaSerializer(respuestas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
#RespuestaFinal

class RespuestaFinalCreate(generics.ListAPIView):
    serializer_class = RespuestaFinalSerializer

    def get_queryset(self):
        estudiante_id = self.request.query_params.get('estudiante_id', None)
        if estudiante_id is not None:
            return RespuestaFinal.objects.filter(estudiante_id=estudiante_id) # pylint: disable=no-member
        return RespuestaFinal.objects.all() # pylint: disable=no-member

    def post(self, request, *args, **kwargs):
        estudiante_id = request.data.get('estudiante')
        pregunta = request.data.get('pregunta')
        opcion_elegida = request.data.get('opcion_elegida')

        if not estudiante_id or not pregunta or not opcion_elegida:
            return Response({"error": "Faltan datos necesarios"}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la nueva respuesta
        respuesta = RespuestaFinal.objects.create( # pylint: disable=no-member
            estudiante_id=estudiante_id,
            pregunta=pregunta,
            opcion_elegida=opcion_elegida
        )

        # Serializar la respuesta creada
        serializer = RespuestaFinalSerializer(respuesta)

        # Devolver la respuesta creada en la respuesta HTTP
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class RespuestasFinalPorEstudiante(APIView):
    def get(self, request):
        estudiante_id = request.GET.get('estudiante_id')
        if not estudiante_id:
            return Response({'error': 'estudiante_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        respuestas = RespuestaFinal.objects.filter(estudiante_id=estudiante_id) # pylint: disable=no-member
        serializer = RespuestaFinalSerializer(respuestas, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    




# Iniciar registro de tiempo RA
class TiempoRAInicioView(APIView):
    def post(self, request):
        estudiante_id = request.data.get('estudiante')
        hora_inicio_str = request.data.get('hora_inicio')

        if not estudiante_id or not hora_inicio_str:
            return Response({"error": "Se requiere 'estudiante' y 'hora_inicio'"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            hora_inicio = datetime.strptime(hora_inicio_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        except ValueError:
            return Response({"error": "Formato de hora_inicio inválido. Usa ISO 8601 con 'Z'."}, status=status.HTTP_400_BAD_REQUEST)

        tiempo_ra = TiempoRA.objects.create(  # pylint: disable=no-member
            estudiante_id=estudiante_id,
            hora_inicio=hora_inicio
        )

        return Response({"mensaje": "Inicio registrado", "tiempo_ra_id": tiempo_ra.id}, status=status.HTTP_201_CREATED)


# Finalizar registro de tiempo RA
class TiempoRAFinView(APIView):
    def post(self, request):
        try:
            tiempo_ra_id = request.data.get("tiempo_ra_id")
            hora_fin_str = request.data.get("hora_fin")

            tiempo_ra = TiempoRA.objects.get(id=tiempo_ra_id)  # pylint: disable=no-member

            hora_fin = datetime.strptime(hora_fin_str, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            tiempo_ra.hora_fin = hora_fin

            tiempo_ra.save()  # Calcula duración correctamente en el modelo
            return Response({"mensaje": "Tiempo RA finalizado correctamente"})
        except Exception as e:
            import traceback
            return Response({
                "error": str(e),
                "trace": traceback.format_exc(),
                "datos_recibidos": request.data
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class DuracionRAView(APIView):
    def get(self, request):
        estudiante_id = request.GET.get('estudiante_id')
        if not estudiante_id:
            return Response({'error': 'estudiante_id es requerido'}, status=status.HTTP_400_BAD_REQUEST)

        tiempo_ra = TiempoRA.objects.filter(estudiante_id=estudiante_id, duracion__isnull=False).order_by('-fecha').first() # pylint: disable=no-member
        if not tiempo_ra:
            return Response({'error': 'No se encontró duración registrada'}, status=status.HTTP_404_NOT_FOUND)

        duracion = str(tiempo_ra.duracion)  # formato HH:MM:SS
        return Response({'duracion': duracion})