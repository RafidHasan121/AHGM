from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated

from UserApp.models import Employee, project, shifts, task
from UserApp.serializers import EmployeeSerializer, ProjectSerializer, ShiftsSerializer, TaskSerializer
# Create your views here.

class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = ['post', 'get', 'put', 'delete']
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]
                    
        return [permission() for permission in permission_classes]
    
class projectViewSet(ModelViewSet):
    queryset = project.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['post', 'get', 'put', 'delete']
    permission_classes = [IsAdminUser]
    
    
    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]
                    
        return [permission() for permission in permission_classes]
    
class taskViewSet(ModelViewSet):
    queryset = task.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ['post', 'get', 'put', 'delete']
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]
                    
        return [permission() for permission in permission_classes]

class shiftsViewSet(ModelViewSet):
    queryset = shifts.objects.all()
    serializer_class = ShiftsSerializer
    http_method_names = ['post', 'get', 'put', 'delete']
    permission_classes = [IsAdminUser]
    
    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]
                    
        return [permission() for permission in permission_classes]
