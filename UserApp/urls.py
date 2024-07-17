from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.SimpleRouter()
router.register(r'emp', EmployeeViewSet)
router.register(r'project', projectViewSet)
router.register(r'task', taskViewSet)
router.register(r'shifts', shiftsViewSet)


urlpatterns = [
    path('', include(router.urls)),
    # path("invite/", invite, name="invite"),
]
