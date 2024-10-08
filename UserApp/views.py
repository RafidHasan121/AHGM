from datetime import datetime
from django.shortcuts import render
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth.hashers import make_password, check_password
from rest_framework.viewsets import ModelViewSet
from Backend.custom_renderer import CustomJSONRenderer
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.decorators import api_view, permission_classes, renderer_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from UserApp.models import Attendance, Employee, User, project, shifts, task
from UserApp.serializers import AttendanceListSerializer, EmployeeSerializer, ProjectSerializer, ShiftsSerializer, TaskSerializer, AttendanceSerializer, UserSerializer

# Create your views here.


class AdminViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'patch']
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomJSONRenderer]

    # def get_permissions(self):
    #     if self.action == 'retrieve' or 'list':
    #         permission_classes = [IsAuthenticated]

    #     return [permission() for permission in permission_classes]

    def get_queryset(self):
        if self.action == 'list':
            self.queryset = self.queryset.filter(id=self.request.user.id)

        return self.queryset


class EmployeeViewSet(ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]
    renderer_classes = [CustomJSONRenderer]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def update(self, request, *args, **kwargs): 
        partial = kwargs.pop('partial', False)
        instance = self.queryset.get(user=kwargs['pk'])
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        instance = self.queryset.get(user=kwargs['pk'])
        self.perform_destroy(instance)
        serializer = EmployeeSerializer(instance)
        return Response(serializer.data, status=200)


class projectViewSet(ModelViewSet):
    queryset = project.objects.all()
    serializer_class = ProjectSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]
    renderer_classes = [CustomJSONRenderer]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        data = project.objects.all()
        serializer = ProjectSerializer(data, many=True)
        return Response(serializer.data, status=200)


class taskViewSet(ModelViewSet):
    queryset = task.objects.all()
    serializer_class = TaskSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]
    renderer_classes = [CustomJSONRenderer]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        if request.data.get('employees'):
            user_ids = request.data.pop('employees')
            id_list = []
            try:
                for each in user_ids:
                    id_list.append(Employee.objects.get(user=each).id)
            except:
                return Response("User not found", status=404)
            request.data.update({'employees': id_list})

        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        if request.data.get('employees'):
            user_ids = request.data.pop('employees')
            id_list = []
            try:
                for each in user_ids:
                    id_list.append(Employee.objects.get(user=each).id)
            except:
                return Response("User not found", status=404)
            request.data.update({'employees': id_list})

        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        project = instance.project
        self.perform_destroy(instance)
        serializer = TaskSerializer(
            task.objects.filter(project=project), many=True)
        return Response(serializer.data, status=200)


class shiftsViewSet(ModelViewSet):
    queryset = shifts.objects.all()
    serializer_class = ShiftsSerializer
    http_method_names = ['post', 'get', 'patch', 'delete']
    permission_classes = [IsAdminUser]
    renderer_classes = [CustomJSONRenderer]

    def get_permissions(self):
        if self.action == 'retrieve' or 'list':
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        serializer = ShiftsSerializer(
            shifts.objects.all(), many=True)
        return Response(serializer.data, status=200)


class attendanceViewSet(ModelViewSet):
    queryset = Attendance.objects.all()
    serializer_class = AttendanceSerializer
    http_method_names = ['post', 'patch']
    permission_classes = [IsAuthenticated]
    renderer_classes = [CustomJSONRenderer]

    def create(self, request, *args, **kwargs):
        user_id = request.data.pop('employee')
        emp = Employee.objects.get(user=user_id)
        request.data.update({'employee': emp.id})
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        attendance_object = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response({'is_active': True,
                         'id': attendance_object.id}, status=201, headers=headers)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response({'is_active': False}, status=200)


@api_view(['GET'])
@renderer_classes([CustomJSONRenderer])
@permission_classes([IsAuthenticated])
def get_attendance(request):
    if not request.query_params.get('year') or not request.query_params.get('month'):
        return Response(status=400)

    if request.query_params.get('employee'):
        queryset = Attendance.objects.filter(employee=request.query_params['employee'], checkIn_date__year=request.query_params[
                                             'year'], checkIn_date__month=request.query_params['month']).order_by('-checkIn_date').order_by('checkIn_time')
        serializer = AttendanceSerializer(queryset, many=True)
        return Response(serializer.data)
    else:
        queryset = Attendance.objects.filter(
            checkIn_date__year=request.query_params['year'], checkIn_date__month=request.query_params['month']).distinct('employee')
        serializer = AttendanceListSerializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['GET'])
@renderer_classes([CustomJSONRenderer])
def status_check(request):
    emp = request.query_params.get('employee')
    if not emp:
        return Response(status=404)
    try:
        instance = Attendance.objects.filter(
            employee__user=emp).latest('checkIn_date')
    except:
        return Response({'is_active': False}, status=200)
    if not instance.checkOut_time:
        R = {'is_active': True,
             'id': instance.id}
    else:
        R = {'is_active': False}
    return Response(R, status=200)


@api_view(['POST', 'GET'])
@renderer_classes([CustomJSONRenderer])
def auth(request):
    if request.method == 'POST':
        phone = request.data.get('phone')
        password = request.data.get('password')
        user = User.objects.filter(phone=phone).first()
        if user is None:
            return Response(status=404)
        if check_password(password, user.password):
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
            return Response(status=403)
    else:
        try:
            Token.objects.filter(user=request.user).delete()
        except:
            return Response(status=400)
        return Response(status=200)


@api_view(['GET'])
@renderer_classes([CustomJSONRenderer])
def task_list_project_filter(request):
    queryset = task.objects.filter(project=request.query_params.get('project'))
    serializer = TaskSerializer(queryset, many=True)
    return Response(serializer.data, status=200)


@api_view(['GET'])
@renderer_classes([CustomJSONRenderer])
def task_list_emp_filter(request):
    if request.user == AnonymousUser() or request.user.is_staff:
        return Response(status=401)
    queryset = task.objects.filter(employees__user=request.user)
    serializer = TaskSerializer(queryset, many=True)
    return Response(serializer.data, status=200)
