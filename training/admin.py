from django.contrib import admin
from .models import TrainingMaterial, TrainingAssignment, TrainingLog


class TrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'media_type', 'status', 'created_at')
    list_filter = ('media_type', 'status')
    search_fields = ('title', 'description')


class TrainingAssignmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'material', 'assigned_at')
    list_filter = ('assigned_at',)
    search_fields = ('employee__emp_name', 'material__title')


class TrainingLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'employee', 'material', 'login_time', 'logout_time', 'time_spent', 'status')
    list_filter = ('status',)
    search_fields = ('employee__emp_name', 'material__title')


admin.site.register(TrainingMaterial, TrainingMaterialAdmin)
admin.site.register(TrainingAssignment, TrainingAssignmentAdmin)
admin.site.register(TrainingLog, TrainingLogAdmin)
