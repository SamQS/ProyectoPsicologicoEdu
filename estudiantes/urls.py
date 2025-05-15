from django.urls import path
from .views import EstudianteListCreate, RespuestaCreate, RespuestasPorEstudiante, RespuestaFinalCreate, RespuestasFinalPorEstudiante, TiempoRAFinView, TiempoRAInicioView, DuracionRAView

urlpatterns = [
    path('api/estudiantes/', EstudianteListCreate.as_view(), name='estudiantes'),
    path('api/respuestas/', RespuestaCreate.as_view(), name='crear_respuesta'),
    path('api/respuestas/<int:estudiante_id>/', RespuestasPorEstudiante.as_view(), name='respuestas-por-estudiante'),
    path('api/postrespuestas/', RespuestaFinalCreate.as_view(), name='crear_respuesta'),
    path('api/postrespuestas/<int:estudiante_id>/', RespuestasFinalPorEstudiante.as_view(), name='respuestas-por-estudiante'),
    path('ra/inicio/', TiempoRAInicioView.as_view(), name='inicio_ra'),
    path('ra/fin/', TiempoRAFinView.as_view(), name='fin_ra'),
    path('ra/duracion/', DuracionRAView.as_view(), name='duracion-ra'),
]
