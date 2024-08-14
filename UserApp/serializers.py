from datetime import timedelta
from rest_framework import serializers
from UserApp.models import Employee, User, Attendance, location, project, shifts, task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'photo', 'designation', 'address')

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    shift = serializers.PrimaryKeyRelatedField(queryset=shifts.objects.all(), write_only=True, allow_null=True, required=False)
    get_shift = ShiftSerializer(source='shift', read_only=True)
    
    class Meta:
        model = Employee
        fields = ('user', 'shift', 'get_shift')

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = User.objects.create(**user_data)
        employee = Employee.objects.create(user=user, **validated_data)
        return employee

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = location
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    location = LocationSerializer()
    task_count = serializers.SerializerMethodField()

    def get_task_count(self, obj):
        return task.objects.filter(project=obj).count()

    class Meta:
        model = project
        fields = ('id', 'name', 'description', 'deadline', 'location', 'task_count')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location_object = location.objects.create(**location_data)
        project_object = project.objects.create(location=location_object, **validated_data)
        return project_object

class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_location = LocationSerializer(source='project.location', read_only=True)
    employee_list = EmployeeSerializer(source="employees", many=True, read_only=True)
    employees = serializers.PrimaryKeyRelatedField(many=True, write_only=True, allow_empty=False, queryset=Employee.objects.all())
    class Meta:
        model = task
        fields = ('id', 'name', 'description', 'project', 'project_name', 'project_location', 'deadline','employee_list', 'employees')

class ShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.user.name', read_only=True)
    designation = serializers.CharField(source='employee.user.designation', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ('id', 'employee', 'checkIn_time', 'checkIn_location_lat', 'checkIn_location_long',
                  'checkOut_time', 'checkOut_location_lat', 'checkOut_location_long', 'name', 'designation')
    
        
# class AttendanceSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = attendance
#         fields = '__all__'


class AttendanceListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.user.name', read_only=True)
    designation = serializers.CharField(source='employee.user.designation', read_only=True)
    attendance = serializers.SerializerMethodField()
    late = serializers.SerializerMethodField()
    overtime = serializers.SerializerMethodField()

    def get_attendance(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time

        # If the shift ends on the next day
        if end < start:
            # Filter records for attendance on the start day
            attendance_count_day1 = self.queryset.filter(
                employee=obj.employee, checkIn_time__gte=start, checkIn_time__lte=start +
                timedelta(minutes=20)
            ).count()

            # Filter records for attendance on the end day
            attendance_count_day2 = self.queryset.filter(
                employee=obj.employee, checkIn_time__gte=start - timedelta(days=1), checkIn_time__lte=end + timedelta(minutes=20)
            ).count()

            return attendance_count_day1 + attendance_count_day2
        else:
            # Shift does not span to the next day
            attendance_count = self.queryset.filter(
                employee=obj.employee, checkIn_time__gte=start, checkIn_time__lte=start +
                timedelta(minutes=20)
            ).count()

            return attendance_count

    def get_late(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time

        if end < start:
            # Shift spans over midnight
            late_count_day1 = self.queryset.filter(
                employee=obj.employee,
                checkIn_time__gte=start + timedelta(minutes=20),
                checkIn_time__lt=start + timedelta(days=1)
            ).count()

            late_count_day2 = self.queryset.filter(
                employee=obj.employee,
                checkIn_time__gte=start -
                timedelta(days=1) + timedelta(minutes=20),
                checkIn_time__lt=end + timedelta(days=1)
            ).count()

            return late_count_day1 + late_count_day2
        else:
            # Shift does not span over midnight
            late_count = self.queryset.filter(
                employee=obj.employee,
                checkIn_time__gte=start + timedelta(minutes=20),
                checkIn_time__lt=end
            ).count()

            return late_count

    def get_overtime(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time
        total_hours = (end - start).total_seconds() / 3600
        overtime_count = self.queryset.filter(
            employee=obj.employee, checkIn_time__gte=end).count()
        total_overtime = overtime_count * total_hours
        return total_overtime
    
    class Meta:
        model = Attendance
        fields = ('id', 'employee', 'name', 'designation', 'attendance', 'late', 'overtime')
