from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils import timezone
from .models import TrainingMaterial, TrainingAssignment, TrainingLog
from accounts.models import EmployeeMaster
from .serializers import TrainingMaterialSerializer, TrainingAssignmentSerializer, TrainingLogSerializer
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserCustom, IsSelfOrAdmin

# ------------------------- Material Views -------------------------

class TrainingMaterialCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def post(self, request):
        serializer = TrainingMaterialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Material created", "data": serializer.data, "status": 201})
        return Response({"errors": serializer.errors, "status": 400})


class TrainingMaterialListView(APIView):
    # permission_classes = [IsAuthenticated]
    def get(self, request):
        materials = TrainingMaterial.objects.all()
        serializer = TrainingMaterialSerializer(materials, many=True)
        return Response({"data": serializer.data, "status": 200})


class TrainingMaterialUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, material_id):
        try:
            material = TrainingMaterial.objects.get(id=material_id)
            serializer = TrainingMaterialSerializer(material, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Material updated", "data": serializer.data, "status": 200})
            return Response({"errors": serializer.errors, "status": 400})
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Material not found", "status": 404})


class TrainingMaterialSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, material_id):
        try:
            material = TrainingMaterial.objects.get(id=material_id)
            material.status = "deleted"
            material.save()
            return Response({"msg": "Material soft deleted", "status": 200})
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Material not found", "status": 404})


# ------------------------- Assignment Views -------------------------

class AssignTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    @transaction.atomic
    def post(self, request):
        employee_id = request.data.get('employee_profile_id')
        material_ids = request.data.get('material_ids', [])

        try:
            employee = EmployeeMaster.objects.get(id=employee_id)
            created = []

            for material_id in material_ids:
                material = TrainingMaterial.objects.get(id=material_id)
                assignment, was_created = TrainingAssignment.objects.get_or_create(employee=employee, material=material)
                if was_created:
                    created.append(material.title)

            return Response({
                "msg": f"Assigned {len(created)} new materials",
                "assigned": created,
                "status": 201
            })
        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Invalid employee ID", "status": 404})
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Invalid material ID", "status": 404})
        except Exception as e:
            return Response({"error": str(e), "status": 400})


class TrainingAssignmentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, assignment_id):
        try:
            assignment = TrainingAssignment.objects.get(id=assignment_id)
            serializer = TrainingAssignmentSerializer(assignment, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Assignment updated", "data": serializer.data, "status": 200})
            return Response({"errors": serializer.errors, "status": 400})
        except TrainingAssignment.DoesNotExist:
            return Response({"error": "Assignment not found", "status": 404})


class TrainingAssignmentSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, assignment_id):
        try:
            assignment = TrainingAssignment.objects.get(id=assignment_id)
            assignment.is_completed = True
            assignment.save()
            return Response({"msg": "Assignment marked completed (soft deleted)", "status": 200})
        except TrainingAssignment.DoesNotExist:
            return Response({"error": "Assignment not found", "status": 404})


# ------------------------- Log Views -------------------------

class StartTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def post(self, request):
        employee_id = request.data.get('employee_profile_id')
        material_id = request.data.get('material_id')

        try:
            employee = EmployeeMaster.objects.get(id=employee_id)
            material = TrainingMaterial.objects.get(id=material_id)

            TrainingLog.objects.create(
                employee=employee,
                material=material,
                login_time=timezone.now(),
                status='in_progress'
            )

            return Response({"msg": "Training started", "status": 201})
        except Exception as e:
            return Response({"error": str(e), "status": 400})


class EndTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsS  elfOrAdmin]

    def post(self, request):
        employee_id = request.data.get('employee_profile_id')
        material_id = request.data.get('material_id')

        try:
            log = TrainingLog.objects.filter(
                employee_id=employee_id,
                material_id=material_id,
                logout_time__isnull=True
            ).latest('login_time')

            log.logout_time = timezone.now()
            log.time_spent = log.logout_time - log.login_time
            log.status = "completed"
            log.save()

            TrainingAssignment.objects.filter(
                employee_id=employee_id,
                material_id=material_id
            ).update(is_completed=True)

            return Response({"msg": "Training ended", "status": 200})
        except TrainingLog.DoesNotExist:
            return Response({"error": "No active training session found", "status": 404})
        except Exception as e:
            return Response({"error": str(e), "status": 400})


class TrainingLogUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, log_id):
        try:
            log = TrainingLog.objects.get(id=log_id)
            serializer = TrainingLogSerializer(log, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"msg": "Log updated", "data": serializer.data, "status": 200})
            return Response({"errors": serializer.errors, "status": 400})
        except TrainingLog.DoesNotExist:
            return Response({"error": "Log not found", "status": 404})


class TrainingLogSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, log_id):
        try:
            log = TrainingLog.objects.get(id=log_id)
            log.status = "cancelled"
            log.save()
            return Response({"msg": "Log cancelled (soft deleted)", "status": 200})
        except TrainingLog.DoesNotExist:
            return Response({"error": "Log not found", "status": 404})


# ------------------------- Employee-Specific Views -------------------------

class MyMaterialsView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]

    def get(self, request, employee_profile_id):
        try:
            employee = EmployeeMaster.objects.get(id=employee_profile_id)
            assignments = TrainingAssignment.objects.filter(employee=employee)
            data = [{
                "material_id": assign.material.id,
                "title": assign.material.title,
                "media_type": assign.material.media_type,
                "media": assign.material.media.url if assign.material.media else None,
                "is_completed": assign.is_completed
            } for assign in assignments]

            return Response({"data": data, "status": 200})
        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Invalid employee ID", "status": 404})
