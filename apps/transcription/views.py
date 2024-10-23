import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .api.transcription import generate_transcription_files, load_dictionary, load_replacement_dict

class TranscriptionAPIView(APIView):
    def post(self, request):
        # Construir rutas a partir del directorio static
        source_dir = os.path.join(settings.STATIC_ROOT, "input/")
        target_dir = os.path.join(settings.STATIC_ROOT, "output")
        reviewed_dir = os.path.join(settings.STATIC_ROOT, "reviewed")
        dict_file = os.path.join(settings.STATIC_ROOT, "dictionary.txt")
        replacements_file = os.path.join(settings.STATIC_ROOT, "replacements.csv")

        # Verificación de existencia de directorios y archivos
        for directory in [source_dir, target_dir, reviewed_dir]:
            if not os.path.exists(directory):
                return Response({'resultado': False, 'error': f'El directorio no existe: {directory}'}, status=status.HTTP_400_BAD_REQUEST)
        
        for file in [dict_file, replacements_file]:
            if not os.path.isfile(file):
                return Response({'resultado': False, 'error': f'El archivo no existe: {file}'}, status=status.HTTP_400_BAD_REQUEST)

        # Cargar los diccionarios
        try:
            word_dict = load_dictionary(dict_file)
            replacement_dict = load_replacement_dict(replacements_file)
        except Exception as e:
            return Response({'resultado': False, 'error': f'Error al cargar los diccionarios: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Generar archivos de transcripción
        try:
            print("Diccionario de palabras:", word_dict)
            print("Diccionario de reemplazos:", replacement_dict)
            generate_transcription_files(source_dir, target_dir, reviewed_dir, 
                                          word_dict=word_dict, replacement_dict=replacement_dict)
            return Response({'resultado': True}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'resultado': False, 'error': f'Error al generar transcripciones: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)