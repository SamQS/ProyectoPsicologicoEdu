import openai
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import os
import tempfile
import traceback  # Para ver errores más detalladamente
from django.conf import settings
from google.oauth2 import service_account
from google.cloud import texttospeech, speech


openai.api_key = os.environ.get("OPENAI_API_KEY")

print("ENV loaded:", os.environ.get("GOOGLE_CREDENTIALS_JSON") is not None)
def get_google_credentials():
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    info = json.loads(credentials_json)

    print("Private key before replace snippet:", info['private_key'][:50])

    # Forzar reemplazo de \n
    info['private_key'] = info['private_key'].replace('\\n', '\n')

    print("Private key after replace snippet:", info['private_key'][:50])

    credentials = service_account.Credentials.from_service_account_info(info)
    return credentials

@csrf_exempt
def chat_gpt(request):
    if request.method == "POST":
        body = json.loads(request.body)
        mensaje_usuario = body.get("mensaje")

        # Prompt base
        prompt = f"Eres un estudiante de secundaria hablando con otro. Responde de forma natural. Mensaje: {mensaje_usuario}"

        try:
            respuesta = openai.ChatCompletion.create(  # pylint: disable=no-member
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un estudiante de secundaria amigable y empático. Estás teniendo una conversación natural con otro estudiante, y tus respuestas deben sonar casuales y cercanas.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            texto_respuesta = respuesta.choices[0].message["content"]

            # Convertir el texto a audio con Google TTS
            credentials = get_google_credentials()
            client = texttospeech.TextToSpeechClient(credentials=credentials)

            # Configuración de entrada
            input_text = texttospeech.SynthesisInput(text=texto_respuesta)
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-ES",  # Español de España
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,  # Voz femenina
                name="es-ES-Standard-A",  # Especificar la voz Wavenet femenina (cambiar si es necesario)
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            # Realiza la solicitud de conversión a audio
            response = client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            # Guardar el archivo de audio en la carpeta media
            media_path = os.path.join(settings.MEDIA_ROOT, "respuesta_audio.mp3")
            with open(media_path, "wb") as out:
                out.write(response.audio_content)

            # Construir la URL absoluta para el archivo de audio
            audio_url = request.build_absolute_uri(
                settings.MEDIA_URL + "respuesta_audio.mp3"
            ).replace("http://", "https://")

            # Devolver la respuesta con el texto y la URL del audio
            return JsonResponse(
                {
                    "texto": texto_respuesta,
                    "audio_url": audio_url,  # Devuelve la URL del archivo de audio
                }
            )

        except Exception as e:
            print("ERROR DETECTADO:")
            traceback.print_exc()  # Imprime el stacktrace en los logs de Railway
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)


# voz


@csrf_exempt
def voz_gpt(request):
    if request.method == "POST":
        audio = request.FILES.get("audio")
        if not audio:
            return JsonResponse({"error": "No se recibió archivo de audio"}, status=400)

        # Guardar archivo de audio temporalmente
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio:
            for chunk in audio.chunks():
                temp_audio.write(chunk)
            temp_audio_path = temp_audio.name

        try:
            # Usar Speech-to-Text para convertir a texto
            credentials = get_google_credentials()
            speech_client = speech.SpeechClient(credentials=credentials)

            with open(temp_audio_path, "rb") as audio_file:
                content = audio_file.read()

            audio_recognition = speech.RecognitionAudio(content=content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=44100,
                language_code="es-ES",
            )

            response = speech_client.recognize(config=config, audio=audio_recognition)
            mensaje_usuario = (
                response.results[0].alternatives[0].transcript
                if response.results
                else ""
            )

            if not mensaje_usuario:
                return JsonResponse({"error": "No se pudo reconocer voz"}, status=400)

            # Reusar lógica de GPT y TTS
            prompt = f"Eres un estudiante de secundaria hablando con otro. Responde de forma natural. Mensaje: {mensaje_usuario}"

            respuesta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un estudiante de secundaria amigable y empático. Estás teniendo una conversación natural con otro estudiante, y tus respuestas deben sonar casuales y cercanas.",
                    },
                    {"role": "user", "content": prompt},
                ],
            )
            texto_respuesta = respuesta.choices[0].message["content"]

            tts_client = texttospeech.TextToSpeechClient(credentials=credentials)
            input_text = texttospeech.SynthesisInput(text=texto_respuesta)
            voice = texttospeech.VoiceSelectionParams(
                language_code="es-ES",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                name="es-ES-Standard-A",
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3
            )

            tts_response = tts_client.synthesize_speech(
                input=input_text, voice=voice, audio_config=audio_config
            )

            media_path = os.path.join(settings.MEDIA_ROOT, "respuesta_audio.mp3")
            with open(media_path, "wb") as out:
                out.write(tts_response.audio_content)

            audio_url = request.build_absolute_uri(
                settings.MEDIA_URL + "respuesta_audio.mp3"
            ).replace("http://", "https://")

            return JsonResponse({"texto": texto_respuesta, "audio_url": audio_url})

        except Exception as e:
            print("ERROR DETECTADO:")
            traceback.print_exc()  # Imprime el stacktrace en los logs de Railway
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Método no permitido"}, status=405)