from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.SimpleRouter()
router.register(r'emp', EmployeeViewSet)
router.register(r'adm', AdminViewSet)
router.register(r'project', projectViewSet)
router.register(r'task', taskViewSet)
router.register(r'shifts', shiftsViewSet)
router.register(r'attendance', attendanceViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("status/", status_check, name="Status Check"),
    path("auth/", auth, name="Login/Logout"),
    path("tasklist/", task_list, name="Task List by Project"), 
]
