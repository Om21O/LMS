from rest_framework import serializers
from .models import *


class TrainingMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingMaterial
        fields = '__all__'


class TrainingAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAssignment
        fields = '__all__'


class TrainingLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingLog
        fields = '__all__'
        read_only_fields = ['time_spent', 'status', 'created_at', 'updated_at', 'logout_time']
