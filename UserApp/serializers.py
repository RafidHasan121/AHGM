from rest_framework import serializers
from UserApp.models import Employee, User, project, shifts, task

# class UserSerializer(ModelSerializer):
#     class Meta:
#         model = User
#         fields = '('name', 'phone', 'photo', 'is_staff', 'designation')'

class EmployeeSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    name = serializers.CharField(source='user.name')
    phone = serializers.CharField(source='user.phone')
    photo = serializers.ImageField(source='user.photo', required=False)
    designation = serializers.CharField(source='user.designation')
    
    class Meta:
        model = Employee
        fields = ('name', 'password', 'phone', 'photo','designation', 'def_shifts', 'def_project', 'fingerprint')

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = project
        fields = '__all__'
        
class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = task
        fields = '__all__'
        
class ShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'