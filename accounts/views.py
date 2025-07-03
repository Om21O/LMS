from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password
from .models import CustomUser, EmployeeMaster

# ✅ Create Admin
class CreateAdminView(APIView):
    def post(self, request):
        data = request.data
        try:
            user = CustomUser.objects.create(
                username=data['username'],
                email=data['email'],
                mobile=data['mobile'],
                is_admin=True,
                is_employee=False,
                password=make_password(data['password']),
            )
            return Response({"msg": "Admin created", "user_id": user.id}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class CreateEmployeeView(APIView):
    def post(self, request):
        data = request.data
        try:
            # Check if the user already exists
            if CustomUser.objects.filter(username=data['username']).exists():
                return Response({"error": "Username already exists"}, status=400)
            user = CustomUser.objects.create(
                username=data['username'],
                email=data['email'],
                mobile=data['mobile'],
                is_admin=False,
                is_employee=True,
                password=make_password(data['password']),
            )

            
            EmployeeMaster.objects.create(
                user=user,
                emp_name=data['emp_name'],
                designation=data['designation'],
                department=data['department'],
                branch=data['branch'],
                mobile=data['mobile'],
                email=data['email'],
                address=data['address'],
                city=data['city'],
                country=data['country'],
            )

            return Response({"msg": "Employee created", "user_id": user.id}, status=201)
        except Exception as e:
            return Response({"error": str(e)}, status=400)
