from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status,permissions
from django.contrib.auth.hashers import make_password
from .models import *
from rest_framework.permissions import IsAuthenticated
from .permissions import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate



class LoginView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate( username=username, password=password)

        if user is not None:
            try:
                role = user.role_connector  # fetch UserRoleConnector
                is_admin = role.is_admin
                is_employee = role.is_employee
                if is_admin:
                    user_role = "admin"
                elif is_employee:
                    user_role = "employee"
                else:
                    user_role = "unknown"
            except Exception as e:
                return Response({"error": "User role not configured", "status": 400})

            refresh = RefreshToken.for_user(user)
            return Response({
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
                "user_role": user_role,
            })
        else:
            return Response({"error": "Invalid credentials", "status": 400})


class LogoutView(APIView):
    #permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "Logout successful", "status": 200})
        except KeyError:
            return Response({"error": "Refresh token is required",  "status": 400})
        except Exception as e:
            return Response({"error": str(e), "status": 400})


#                                          # Admin Views
# Create Admin 


class CreateAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def post(self, request):
        data = request.data
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        # Check for duplicates
        if User.objects.filter(username=username).exists():
            return Response({"error": "Username already exists"}, status=400)

        if User.objects.filter(email=email).exists():
            return Response({"error": "Email already exists"}, status=400)

        try:
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password
            )

            user_profile = EmployeeProfile.objects.create(
                user=user,
                is_admin=True
            )

            return Response({
                "msg": "Admin created successfully",
                "user_id": user.id,
                "admin_profile_id": user_profile.id
            }, status=201)

        except Exception as e:
            return Response({
                "error": str(e)
            }, status=400)
# Get Admin Details
class GetAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        admin = request.user
        return Response({
            "id": admin.id,
            "username": admin.username,
            "email": admin.email
            
            ,"status":200
        } )

# Update Admin
class UpdateAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def put(self, request):
        admin = request.user
        admin.username = request.data.get("username", admin.username)
        admin.email = request.data.get("email", admin.email)
       # admin.mobile = request.data.get("mobile", admin.mobile)
        if request.data.get("password"):
            admin.password = make_password(request.data["password"])
        admin.save()
        return Response({"msg": "Admin updated", "status": 200}, )

# Soft Delete Admin (only by another Admin)
class DeleteAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def delete(self, request, pk):
        try:
            admin_user = User.objects.get(pk=pk, is_admin=True)
            if request.user.id == admin_user.id:
                return Response({"error": "You can't delete yourself", "status":200})
            admin_user.is_active = False
            admin_user.save()
            return Response({"msg": "Admin deleted" ,"status":200})
        except User.DoesNotExist:
            return Response({"error": "Admin not found ", "status":404})

class GetSpecificAdminView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if not hasattr(user, "role_connector") or not user.role_connector.is_admin:
                return Response({"error": "User is not an admin", "status": 403})

            return Response({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "status": 200
            })

        except User.DoesNotExist:
            return Response({"error": "Admin not found", "status": 404})
#                                        EMPLOYEE VIEWS
class CreateEmployeeView(APIView):
    # permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def post(self, request):
        data = request.data
        try:
            # Check if the user already exists
            if User.objects.filter(username=data['username']).exists():
                return Response({"error": "Username already exists","status":400}, )
            user =User.objects.create(
                username=data['username'],
                email=data['email'],
                # mobile=data['mobile'],
                password=make_password(data['password']),
            )

            
            emp_profile =EmployeeMaster.objects.create(
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
            # Create a profile for the employee
            EmployeeProfile.objects.create(
                user=user,
                is_employee=True,
            )

            return Response({"msg": "Employee created","user_id": user.id,
                "employee_profile_id":emp_profile.id ,"status":201 },)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class GetAllEmployeesView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def get(self, request):
        try:
            employees = EmployeeProfile.objects.filter(is_employee=True).select_related('user')
            result = []

            for emp_profile in employees:
                try:
                    master = EmployeeMaster.objects.get(user=emp_profile.user)
                    result.append({
                        "user_id": emp_profile.user.id,
                        "username": emp_profile.user.username,
                        "email": emp_profile.user.email,
                        "emp_name": master.emp_name,
                        "designation": master.designation,
                        "department": master.department,
                        "branch": master.branch,
                        "mobile": master.mobile,
                        "address": master.address,
                        "city": master.city,
                        "country": master.country,
                    })
                except EmployeeMaster.DoesNotExist:
                    continue  # skip if the master data is missing

            return Response({"employees": result,"Status":200})

        except Exception as e:
            return Response({"error": str(e),"Status":400})

class UpdateEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def put(self, request, pk):
        try:
            emp = EmployeeMaster.objects.get(pk=pk)
            self.check_object_permissions(request, emp)

            emp.emp_name = request.data.get("emp_name", emp.emp_name)
            emp.designation = request.data.get("designation", emp.designation)
            emp.department = request.data.get("department", emp.department)
            emp.branch = request.data.get("branch", emp.branch)
            emp.mobile = request.data.get("mobile", emp.mobile)
            emp.email = request.data.get("email", emp.email)
            emp.address = request.data.get("address", emp.address)
            emp.city = request.data.get("city", emp.city)
            emp.country = request.data.get("country", emp.country)
            emp.save()

            return Response({"msg": "Employee updated", "status": 200})
        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})


class DeleteEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]

    def delete(self, request, pk):
        try:
            emp = EmployeeMaster.objects.get(pk=pk)
            emp.user.is_active = False
            emp.user.save()
            return Response({"msg": "Employee soft-deleted", "status": 200})
        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})


class GetSpecificEmployeeView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def get(self, request, pk):
        try:
            employee = EmployeeMaster.objects.get(pk=pk)
            self.check_object_permissions(request, employee)
            return Response({
                "id": employee.id,
                "emp_name": employee.emp_name,
                "designation": employee.designation,
                "department": employee.department,
                "branch": employee.branch,
                "mobile": employee.mobile,
                "email": employee.email,
                "address": employee.address,
                "city": employee.city,
                "country": employee.country,
                "status": 200
            })
        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Employee not found", "status": 404})

