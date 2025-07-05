from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'mobile', 'is_admin', 'is_employee']

class EmployeeMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmployeeMaster
        fields = '__all__'