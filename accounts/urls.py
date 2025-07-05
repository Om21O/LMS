from django.urls import path
from .views import (
    CreateAdminView,
    CreateEmployeeView,
    GetAdminView,
    UpdateAdminView,
    DeleteAdminView,
    GetEmployeeView,
    UpdateEmployeeView,
    DeleteEmployeeView,
    LoginView,
    LogoutView,
    GetSpecificAdminView,
    GetSpecificEmployeeView,
    GetAllEmployeesView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/register/', CreateAdminView.as_view(), name='admin_register'),
    path('employee/register/', CreateEmployeeView.as_view(), name='employee_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('admin/details/', GetAdminView.as_view()),
    path('admin/update/', UpdateAdminView.as_view()),
    path('admin/delete/<str:pk>/', DeleteAdminView.as_view()),
    path('employee/<int:pk>/', GetEmployeeView.as_view()),
    path('employee/update/<int:pk>/', UpdateEmployeeView.as_view()),
    path('employee/delete/<int:pk>/', DeleteEmployeeView.as_view()),
    path('admin/view/<int:pk>/', GetSpecificAdminView.as_view()),
    path('employee/view/<int:pk>/', GetSpecificEmployeeView.as_view()),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('employee/details/', GetAllEmployeesView.as_view(), name='employee_details'),
]
