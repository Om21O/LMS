from django.db import models
from accounts.models import EmployeeMaster  # adjust import if app name differs


class TrainingMaterial(models.Model):
    MEDIA_TYPE_CHOICES = (
        ('pdf', 'PDF'),
        ('image', 'Image'),
        ('youtube', 'YouTube'),
    )

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    media_type = models.CharField(max_length=20, choices=MEDIA_TYPE_CHOICES)
    media = models.TextField()  # Stores file path or YouTube URL
    status = models.CharField(max_length=20, default='active')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table="training_trainingmaterial"

    def __str__(self):
        return self.title


class TrainingAssignment(models.Model):
    employee = models.ForeignKey(
        EmployeeMaster,on_delete=models.DO_NOTHING, related_name='assignments'
    )
    material = models.ForeignKey(
        TrainingMaterial, on_delete=models.DO_NOTHING, related_name='assignments1'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('employee', 'material')
        db_table="training_trainingassignment"

    def __str__(self):
        return f'{self.employee.emp_name} - {self.material.title}'


class TrainingLog(models.Model):
    employee = models.ForeignKey(
        EmployeeMaster,on_delete=models.DO_NOTHING, related_name='training_logs'
    )
    material = models.ForeignKey(
        TrainingMaterial,on_delete=models.DO_NOTHING, related_name='logs'
    )
    login_time = models.DateTimeField()
    logout_time = models.DateTimeField(blank=True, null=True)
    time_spent = models.DurationField(blank=True, null=True)
    status = models.CharField(max_length=50)  # e.g. in_progress, completed
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table="training_traininglog"

    def __str__(self):
        return f'{self.employee.emp_name} - {self.material.title} - {self.status}'


class TrainingSession(models.Model):
    employee = models.ForeignKey(
        EmployeeMaster,on_delete=models.DO_NOTHING, related_name='sessions'
    )
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table="training_trainingsession"

    def __str__(self):
        return f'{self.employee.emp_name} session on {self.started_at.date()}'

