from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .serializers import CallTakerCreateSerializer, CallTakerListSerializer
from ..models import CallTaker
from common.helpers.api_responses import api_response

class createUser(generics.CreateAPIView):
    def create(self, request):
        """Crear un nuevo CallTaker."""
        serializer = CallTakerCreateSerializer(data=request.data)
        if serializer.is_valid():
            call_taker = serializer.save()
            response_data = api_response(True, CallTakerCreateSerializer(call_taker).data, "Successfully created")
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = api_response(False, [], serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)

class ListCallTakers(generics.ListAPIView):
    queryset = CallTaker.objects()  # Asegúrate de usar el modelo aquí
    serializer_class = CallTakerListSerializer

    def get(self, request, *args, **kwargs):
        """Listar todos los CallTakers."""
        call_takers = self.get_queryset()
        serializer = self.get_serializer(call_takers, many=True)
        response_data = api_response(True, serializer.data, "Successfully retrieved")
        return Response(response_data, status=status.HTTP_200_OK)
    
class ListCallTakersByCode(generics.ListAPIView):
    serializer_class = CallTakerListSerializer

    def get_queryset(self):
        code = self.kwargs.get('code')  # Obtiene el código de los parámetros de la URL
        return CallTaker.objects.filter(code=code)  # Filtra por el código proporcionado

    def get(self, request, *args, **kwargs):
        """Listar CallTakers filtrados por code."""
        call_takers = self.get_queryset()
        serializer = self.get_serializer(call_takers, many=True)
        response_data = api_response(True, serializer.data, "Successfully retrieved")
        return Response(response_data, status=status.HTTP_200_OK)