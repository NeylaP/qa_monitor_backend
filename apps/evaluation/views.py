# my_app/views.py

from django.http import JsonResponse
from rest_framework.views import APIView
from .api.evaluation import process_conversations
from common.helpers.api_responses import api_response
from rest_framework.response import Response
from rest_framework import status

class EvaluateAPIView(APIView):
    def post(self, request):
        try:
            process_conversations()
            response_data = api_response(True, [], "Successfully")
                
            return Response(response_data, status=status.HTTP_200_OK)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

