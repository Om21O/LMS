from django.urls import path
from .views import *

urlpatterns = [
    path('materials/create/', TrainingMaterialCreateView.as_view()),
    path('materials/', TrainingMaterialListView.as_view()),
    path('materials/update/<int:material_id>/', TrainingMaterialUpdateView.as_view()),
    path('materials/soft-delete/<int:material_id>/', TrainingMaterialSoftDeleteView.as_view()),
    path('assign/', AssignTrainingView.as_view()),
    path('mymaterials/<int:employee_profile_id>/', MyMaterialsView.as_view()),
    path('start/', StartTrainingView.as_view()),
    path('end/', EndTrainingView.as_view()),
     path('assignment/update/<int:assignment_id>/', TrainingAssignmentUpdateView.as_view()),
    path('assignment/soft-delete/<int:assignment_id>/', TrainingAssignmentSoftDeleteView.as_view()),
    path('log/update/<int:log_id>/', TrainingLogUpdateView.as_view()),
    path('log/soft-delete/<int:log_id>/', TrainingLogSoftDeleteView.as_view()),
    path('session/start/', StartTrainingSessionView.as_view(), name='start-training-session'),
    path('session/end/', EndTrainingSessionView.as_view(), name='end-training-session'),

]
