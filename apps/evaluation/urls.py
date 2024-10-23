from django.urls import path
from .views import EvaluateAPIView
urlpatterns = [
  path("evaluation", EvaluateAPIView.as_view(), name=None),
]