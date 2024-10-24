from django.urls import path
from .views import EvaluateAPIView
from .api.viewsets import EvaluationResultsViewSet
urlpatterns = [
  path("evaluation", EvaluateAPIView.as_view(), name=None),
  path("results", EvaluationResultsViewSet.as_view({'post': 'get_results'}), name=None),
]