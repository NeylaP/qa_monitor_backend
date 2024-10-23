from django.urls import path
from .views import TranscriptionAPIView
urlpatterns = [
  path("transcription", TranscriptionAPIView.as_view(), name=None),
]