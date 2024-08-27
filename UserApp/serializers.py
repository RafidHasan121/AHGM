from datetime import timedelta, datetime
from rest_framework import serializers
from UserApp.models import Employee, User, Attendance, location, project, shifts, task


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password', 'placeholder': 'Password'}
    )
    is_admin = serializers.BooleanField(read_only=True, source='is_staff')

    class Meta:
        model = User
        fields = ('id', 'name', 'phone', 'password', 'photo',
                  'designation', 'address', 'is_admin')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class ShiftSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'

    def create(self, validated_data):
        if validated_data['start_time'] > validated_data['end_time']:
            raise serializers.ValidationError(
                "Start time cannot be greater than end time")
        return super().create(validated_data)


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    shift = serializers.PrimaryKeyRelatedField(
        queryset=shifts.objects.all(), write_only=True, allow_null=True, required=False)
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
        fields = ('id', 'name', 'description',
                  'deadline', 'location', 'task_count')

    def create(self, validated_data):
        location_data = validated_data.pop('location')
        location_object = location.objects.create(**location_data)
        project_object = project.objects.create(
            location=location_object, **validated_data)
        return project_object

    def update(self, instance, validated_data):
        location_data = validated_data.pop('location', None)
        for (key, value) in validated_data.items():
            setattr(instance, key, value)
        if location_data is not None:
            location_object = instance.location
            for (key, value) in location_data.items():
                setattr(location_object, key, value)
            location_object.save()
        instance.save()
        return instance


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_location = LocationSerializer(
        source='project.location', read_only=True)
    employee_list = EmployeeSerializer(
        source="employees", many=True, read_only=True)
    employees = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, allow_empty=True, queryset=Employee.objects.all())

    class Meta:
        model = task
        fields = ('id', 'name', 'description', 'project', 'project_name',
                  'project_location', 'deadline', 'employee_list', 'employees')


class ShiftsSerializer(serializers.ModelSerializer):
    class Meta:
        model = shifts
        fields = '__all__'


class AttendanceSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.user.name', read_only=True)
    designation = serializers.CharField(
        source='employee.user.designation', read_only=True)

    class Meta:
        model = Attendance
        fields = ('id', 'employee', 'checkIn_date', 'checkIn_time', 'checkIn_location_lat', 'checkIn_location_long',
                  'checkOut_date', 'checkOut_time', 'checkOut_location_lat', 'checkOut_location_long', 'name', 'designation')


# class AttendanceSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = attendance
#         fields = '__all__'


class AttendanceListSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='employee.user.name', read_only=True)
    designation = serializers.CharField(
        source='employee.user.designation', read_only=True)
    attendance = serializers.SerializerMethodField()
    late = serializers.SerializerMethodField()
    overtime = serializers.SerializerMethodField()

    def get_attendance(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time

        # If the shift ends on the next day
        if end < start:
            # Filter records for attendance on the start day
            attendance_count_day1 = Attendance.objects.filter(
                employee=obj.employee, checkIn_time__gte=start, checkIn_time__lte=start).count()

            # Filter records for attendance on the end day
            attendance_count_day2 = Attendance.objects.filter(
                employee=obj.employee, checkIn_time__gte=start - timedelta(days=1), checkIn_time__lte=end).count()

            return attendance_count_day1 + attendance_count_day2
        else:
            # Shift does not span to the next day
            attendance_count = Attendance.objects.filter(
                employee=obj.employee, checkIn_time__gte=start, checkIn_time__lte=start).count()

            return attendance_count

    def get_late(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time

        if end < start:
            # Shift spans over midnight
            late_count_day1 = Attendance.objects.filter(
                employee=obj.employee,
                checkIn_time__gte=start,
                checkIn_time__lt=start
            ).count()

            late_count_day2 = Attendance.objects.filter(
                employee=obj.employee,
                checkIn_time__gte=start,
                checkIn_time__lt=end).count()

            return late_count_day1 + late_count_day2
        else:
            # Shift does not span over midnight
            late_count = Attendance.objects.filter(
                employee=obj.employee,
                checkIn_time__gte=start,
                checkIn_time__lt=end).count()

            return late_count

    def get_overtime(self, obj):
        start = obj.employee.shift.start_time
        end = obj.employee.shift.end_time
        new_start = datetime.strptime(str(start), '%H:%M:%S')
        new_end = datetime.strptime(str(end), '%H:%M:%S')
        total_hours = (new_end - new_start).total_seconds() / 3600
        overtime_count = Attendance.objects.filter(
            employee=obj.employee, checkIn_time__gte=end).count()
        total_overtime = overtime_count * total_hours
        return total_overtime

    class Meta:
        model = Attendance
        fields = ('id', 'employee', 'name', 'designation',
                  'attendance', 'late', 'overtime')
