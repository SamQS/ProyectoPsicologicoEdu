from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/chat/', views.chat_gpt, name='chat_gpt'),
    path('api/voz/', views.voz_gpt, name='voz_gpt'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
