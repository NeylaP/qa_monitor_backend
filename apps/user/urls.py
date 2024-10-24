from django.urls import path
from .api.viewsets import createUser, listCallTakers, listCallTakersByCode, updateCallTaker
urlpatterns = [
  path("users/create_calltaker", createUser.as_view(), name=None),
  path("users/calltaker/bycode/<str:code>", listCallTakersByCode.as_view(), name=None),
  path("users/all_calltaker", listCallTakers.as_view(), name=None),
  path('users/calltaker/update/<str:pk>', updateCallTaker.as_view(), name=None),
]