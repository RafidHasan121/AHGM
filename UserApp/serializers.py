from datetime import timedelta
from rest_framework import serializers
from UserApp.models import Employee, User, Attendance, location, project, shifts, task

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'phone', 'photo', 'designation', 'address')

class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'

class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    # password = serializers.CharField(write_only=True)
    # name = serializers.CharField(source='user.name')
    # phone = serializers.CharField(source='user.phone')
    # photo = serializers.ImageField(source='user.photo', required=False)
    # address = serializers.CharField(source='user.address', required=False)
    # designation = serializers.CharField(source='user.designation')
    shift = ShiftSerializer()
    
    class Meta:
        model = Employee
        # fields = ('name', 'password', 'phone', 'photo',
        #           'address', 'designation', 'shift')
        fields = ('user', 'shift')

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
        fields = ('name', 'description', 'deadline', 'location', 'task_count')


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_location = LocationSerializer(source='project.location', read_only=True)
    employee_list = EmployeeSerializer(read_only=True, many=True)
    employees = serializers.PrimaryKeyRelatedField(many=True, write_only=True, allow_empty=False, queryset=Employee.objects.all())
    class Meta:
        model = task
        fields = ('name', 'description', 'project', 'project_name', 'project_location', 'deadline','employee_list', 'employees')

class ShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.user.name', read_only=True)
    designation = serializers.CharField(source='employee.user.designation', read_only=True)
    
    class Meta:
        model = Attendance
        fields = ('employee', 'checkIn_time', 'checkIn_location',
                  'checkOut_time', 'checkOut_location', 'name', 'designation')

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
        fields = ('employee', 'name', 'designation', 'attendance', 'late', 'overtime')
