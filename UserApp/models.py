from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _
from .manager import UserManager


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, unique=True)
    photo = models.ImageField(upload_to='user_photos', null=True, blank=True)
    is_staff = models.BooleanField(
        _("staff status"),
        default=False,
        help_text=_(
            "Designates whether the user can log into this admin site."),
    )
    designation = models.CharField(max_length=50)
    address = models.TextField(null=True, blank=True)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = []
    objects = UserManager()


class location (models.Model):
    name = models.CharField(max_length=50, null=True, blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()


class project (models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    deadline = models.DateTimeField()
    location = models.OneToOneField(location, on_delete=models.PROTECT)


class shifts(models.Model):
    name = models.CharField(max_length=50)
    start_time = models.TimeField()
    end_time = models.TimeField()


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shift = models.ForeignKey(
        shifts, on_delete=models.SET_NULL, null=True, blank=True)


class task(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    project = models.ForeignKey(project, on_delete=models.CASCADE)
    deadline = models.DateTimeField()
    employees = models.ManyToManyField(Employee, related_name='employees')


class Attendance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    checkIn_date = models.DateField()
    checkIn_time = models.TimeField()
    checkIn_location_lat = models.FloatField()
    checkIn_location_long = models.FloatField()
    checkOut_date = models.DateField(null=True, blank=True)
    checkOut_time = models.TimeField(null=True, blank=True)
    checkOut_location_lat = models.FloatField(null=True, blank=True)
    checkOut_location_long = models.FloatField(null=True, blank=True)