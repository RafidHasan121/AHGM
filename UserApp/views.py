from datetime import datetime
from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser, IsAuthenticated, AllowAny
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from UserApp.models import Attendance, Employee, User, project, shifts, task
from UserApp.serializers import AttendanceListSerializer, EmployeeSerializer, ProjectSerializer, ShiftsSerializer, TaskSerializer, AttendanceSerializer, UserSerializer
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
# Create your views here.

class AdminViewSet(ModelViewSet):
    queryset = User.objects.filter(is_staff=True)
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch']
    permission_classes = [IsAdminUser]
    
class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs):       
        if not self.request.user.is_staff:
            kwargs.pop('shift', None)
            kwargs.pop('project', None)
            if "password" in kwargs:
                pswrd = kwargs.pop('password')
                self.get_object().user.set_password(pswrd)
                self.get_object().user.save()
        else:
            if kwargs['password']:
                kwargs.pop('password')
                self.get_object().user.set_password("123456")
                self.get_object().user.save()
        
        return super().update(request, *args, **kwargs)


class projectViewSet(ModelViewSet):
    queryset = project.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class taskViewSet(ModelViewSet):
    queryset = task.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class shiftsViewSet(ModelViewSet):
    queryset = shifts.objects.all()
    serializer_class = ShiftsSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]


class attendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    http_method_names = ['post', 'get', 'patch']
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            queryset = self.queryset.filter(checkin_time__year=self.kwargs['year'], checkin_time__month=self.kwargs['month']).distinct('employee')
        if self.action == "retrieve":
            queryset = self.queryset.filter(employee=self.kwargs['employee'], checkin_time__year=self.kwargs['year'], checkin_time__month=self.kwargs['month']).order_by('checkin_time')
        return queryset
    
    def get_serializer_class(self):
        if self.action == 'list':
            serializer =  AttendanceListSerializer  
        else:
            serializer = self.serializer_class
        
        return serializer
    
    def perform_create(self, serializer):
        if serializer.data.get('checkIn_time').date() == datetime.now().date():
            raise PermissionDenied
        serializer.save()
        return Response({'status': False}, status=201, headers=self.headers)
    
    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = Attendance.objects.filter(employee=kwargs['employee']).order_by('-checkIn_time').first()
        if not instance:
            raise PermissionDenied
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({'status': False}, status=200, headers=self.headers)

@api_view(['GET'])
def status_check(request):
    emp = request.query_params.get('employee')
    if not emp:
        raise ObjectDoesNotExist
    instance = Attendance.objects.get(employee=emp).latest('checkIn_time')
    if not instance:
        raise ObjectDoesNotExist
    if instance.checkOut_time:
        R = {'status': True}
    else:
        R = {'status': False}
    return Response(R, status=200)

@api_view(['POST', 'GET'])
def auth(request):
    if request.method == 'POST':
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = User.objects.get(phone=phone)
        if user.check_password(password):
            token = Token.objects.update_or_create(user=user)
            if user.is_staff:
                serializer = UserSerializer(user)
                return Response({'role': "admin",
                                "token": token[0].key,
                                "user": serializer.data}, status=200)
            else:
                employee = Employee.objects.get(user=user)
                serializer = EmployeeSerializer(employee)
                return Response({'role': "employee",
                                "token": token[0].key,
                                "user": serializer.data}, status=200)
        else:
            return Response(status=401)
    else:
        try:
            Token.objects.filter(user=request.user).delete()
        except:
            raise ObjectDoesNotExist
        return Response(status=200)
