from django.urls import path
from .api.viewsets import createUser, ListCallTakers, ListCallTakersByCode
urlpatterns = [
  path("users/create_calltaker", createUser.as_view(), name=None),
  path("users/calltaker/bycode/<str:code>", ListCallTakersByCode.as_view(), name=None),
  path("users/all_calltaker", ListCallTakers.as_view(), name=None),
]