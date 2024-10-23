# my_app/views.py

from django.http import JsonResponse
from rest_framework.views import APIView
from .api.evaluation import process_conversations

class EvaluateAPIView(APIView):
    def post(self, request):
        try:
            process_conversations()
            return JsonResponse({"resultado": "Evaluación completa"}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

