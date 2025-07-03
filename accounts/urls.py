from django.urls import path
from .views import CreateAdminView, CreateEmployeeView

urlpatterns = [
    path('admin/register/', CreateAdminView.as_view(), name='admin_register'),
    path('employee/register/', CreateEmployeeView.as_view(), name='employee_register'),
]
