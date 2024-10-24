import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .api.transcription import generate_transcription_files, load_dictionary, load_replacement_dict
from common.helpers.api_responses import api_response

class TranscriptionAPIView(APIView):
    def post(self, request):
        source_dir = os.path.join(settings.STATIC_ROOT, "input/")
        target_dir = os.path.join(settings.STATIC_ROOT, "output")
        reviewed_dir = os.path.join(settings.STATIC_ROOT, "reviewed")
        dict_file = os.path.join(settings.STATIC_ROOT, "dictionary.txt")
        replacements_file = os.path.join(settings.STATIC_ROOT, "replacements.csv")

        for directory in [source_dir, target_dir, reviewed_dir]:
            if not os.path.exists(directory):
                response_data = api_response(False, [], f'The directory does not exist: {directory}')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
        
        for file in [dict_file, replacements_file]:
            if not os.path.isfile(file):
                response_data = api_response(False, [], f'File does not exist: {file}')
                return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

        try:
            word_dict = load_dictionary(dict_file)
            replacement_dict = load_replacement_dict(replacements_file)
        except Exception as e:
            response_data = api_response(False, [], f'Error loading dictionaries: {str(e)}')
            return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            generate_transcription_files(source_dir, target_dir, reviewed_dir, 
                                          word_dict=word_dict, replacement_dict=replacement_dict)
            return Response(api_response(True, [], "Successfully"), status=status.HTTP_200_OK)
        except Exception as e:
            return Response(api_response(False,[], f'Error when generating transcripts: {str(e)}'), status=status.HTTP_500_INTERNAL_SERVER_ERROR)