from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.models import User




class EmployeeMaster(models.Model):
    user = models.OneToOneField(User, on_delete=models.DO_NOTHING, related_name='employee_profile')
    emp_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    class Meta:
        db_table="accounts_employeemaster"

    def __str__(self):
        return self.emp_name

class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role_connector')
    is_admin = models.BooleanField(default=False)
    is_employee = models.BooleanField(default=False)

    class Meta:
        db_table="accounts_employeeprofile"
    
    def __str__(self):
        return self.user.username