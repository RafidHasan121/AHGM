from django.contrib import admin
from .models import *

admin.site.register(User)
admin.site.register(project)
admin.site.register(task)
admin.site.register(Employee)
admin.site.register(Attendance)
admin.site.register(location)
admin.site.register(shifts)

