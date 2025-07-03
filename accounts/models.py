from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    is_employee = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    email = models.EmailField(unique=True)
    mobile = models.CharField(max_length=15, blank=True)

    def __str__(self):
        return self.username

class EmployeeMaster(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.DO_NOTHING, related_name='employee_profile')
    
    emp_name = models.CharField(max_length=100)
    designation = models.CharField(max_length=100)
    department = models.CharField(max_length=100)
    branch = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    def __str__(self):
        return self.emp_name