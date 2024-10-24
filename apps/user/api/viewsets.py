from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .serializers import CallTakerCreateSerializer, CallTakerListSerializer, CallTakerUpdateSerializer
from ..models import CallTaker
from common.helpers.api_responses import api_response
from mongoengine import DoesNotExist

class createUser(generics.CreateAPIView):
    def create(self, request):
        serializer = CallTakerCreateSerializer(data=request.data)
        if serializer.is_valid():
            call_taker = serializer.save()
            response_data = api_response(True, CallTakerCreateSerializer(call_taker).data, "Successfully created")
            return Response(response_data, status=status.HTTP_201_CREATED)
        response_data = api_response(False, [], serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
class listCallTakers(generics.ListAPIView):
    queryset = CallTaker.objects.all()
    serializer_class = CallTakerListSerializer

    def get(self, request, *args, **kwargs):
        call_takers = self.get_queryset()
        serializer = self.get_serializer(call_takers, many=True)
        response_data = api_response(True, serializer.data, "Successfully retrieved")
        return Response(response_data, status=status.HTTP_200_OK)
class listCallTakersByCode(generics.ListAPIView):
    serializer_class = CallTakerListSerializer

    def get_queryset(self):
        code = self.kwargs.get('code')
        return CallTaker.objects.filter(code=code)

    def get(self, request, *args, **kwargs):
        call_takers = self.get_queryset()
        serializer = self.get_serializer(call_takers, many=True)
        response_data = api_response(True, serializer.data, "Successfully retrieved")
        return Response(response_data, status=status.HTTP_200_OK)
class updateCallTaker(generics.UpdateAPIView):
    serializer_class = CallTakerUpdateSerializer

    def get_object(self):
        call_taker_id = self.kwargs['pk']
        try:
            return CallTaker.objects.get(id=call_taker_id)
        except DoesNotExist:
            return None

    def put(self, request, *args, **kwargs):
        call_taker = self.get_object()
        if call_taker is None:
            response_data = api_response(False, [], "CallTaker not found")
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(call_taker, data=request.data)

        # Asegúrate de llamar a is_valid() antes de acceder a serializer.data
        if serializer.is_valid():
            updated_call_taker = serializer.save()
            response_data = api_response(True, serializer.data, "Successfully updated")
            return Response(response_data, status=status.HTTP_200_OK)

        response_data = api_response(False, [], serializer.errors)
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)