from django.urls import path, re_path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

urlpatterns = [
    path('api/chat/', views.chat_gpt, name='chat_gpt'),
    path('api/voz/', views.voz_gpt, name='voz_gpt'),
] 
# Permitir servir archivos desde /media/ incluso en producción
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]