from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *

# class CustomUserAdmin(UserAdmin):
#     model = CustomUser
#     list_display = ('id', 'username', 'email', 'mobile', 'is_admin', 'is_employee')
#     list_filter = ('is_admin', 'is_employee')

# admin.site.register(CustomUser, CustomUserAdmin)  # ✅ Register with your custom admin class
admin.site.register(EmployeeMaster)
admin.site.register(EmployeeProfile)