from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from .models import TrainingMaterial, TrainingAssignment, TrainingLog
from accounts.models import EmployeeMaster
from .serializers import TrainingMaterialSerializer, TrainingAssignmentSerializer, TrainingLogSerializer
from django.utils import timezone
from datetime import timedelta
from rest_framework.permissions import IsAuthenticated
from accounts.permissions import IsAdminUserCustom, IsSelfOrAdmin

class TrainingMaterialCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def post(self, request):
        data = request.data
        serializer = TrainingMaterialSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Material created", "data": serializer.data}, status=201)
        return Response(serializer.errors, status=400)

#list
class TrainingMaterialListView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def get(self, request):
        materials = TrainingMaterial.objects.all()
        serializer = TrainingMaterialSerializer(materials, many=True)
        return Response(serializer.data, status=200)

class AssignTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    @transaction.atomic
    def post(self, request):
        employee_id = request.data.get('employee_id')
        material_ids = request.data.get('material_ids', [])

        try:
            employee = EmployeeMaster.objects.get(id=employee_id)

            created = []
            for material_id in material_ids:
                material = TrainingMaterial.objects.get(id=material_id)
                assignment, created_flag = TrainingAssignment.objects.get_or_create(
                    employee=employee,
                    material=material
                )
                if created_flag:
                    created.append(material.title)

            return Response({
                "msg": f"Assigned {len(created)} new materials",
                "assigned": created
            }, status=201)

        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Invalid employee ID"}, status=404)
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Invalid material ID"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


class TrainingMaterialUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, material_id):
        try:
            material = TrainingMaterial.objects.get(id=material_id)
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Material not found"}, status=404)

        serializer = TrainingMaterialSerializer(material, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Material updated", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)
    
class TrainingMaterialSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, material_id):
        try:
            material = TrainingMaterial.objects.get(id=material_id)
            material.status = "deleted"  # Soft delete by changing status
            material.save()
            return Response({"msg": "Material soft deleted"}, status=200)
        except TrainingMaterial.DoesNotExist:
            return Response({"error": "Material not found"}, status=404)


class MyMaterialsView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]
    def get(self, request, employee_id):
        try:
            employee = EmployeeMaster.objects.get(id=employee_id)
            assignments = TrainingAssignment.objects.filter(employee=employee)
            data = [{
                "material_id": assign.material.id,
                "title": assign.material.title,
                "media_type": assign.material.media_type,
                "media": assign.material.media,
                "is_completed": assign.is_completed
            } for assign in assignments]

            return Response(data, status=200)

        except EmployeeMaster.DoesNotExist:
            return Response({"error": "Invalid employee ID"}, status=404)


class StartTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]
    def post(self, request):
        employee_id = request.data.get('employee_id')
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

            return Response({"msg": "Training started"}, status=201)

        except Exception as e:
            return Response({"error": str(e)}, status=400)



class EndTrainingView(APIView):
    permission_classes = [IsAuthenticated, IsSelfOrAdmin]
    def post(self, request):
        employee_id = request.data.get('employee_id')
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

            # Mark assignment completed
            TrainingAssignment.objects.filter(
                employee_id=employee_id,
                material_id=material_id
            ).update(is_completed=True)

            return Response({"msg": "Training ended"}, status=200)

        except TrainingLog.DoesNotExist:
            return Response({"error": "No active training session found"}, status=404)
        except Exception as e:
            return Response({"error": str(e)}, status=400)

class TrainingAssignmentUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, assignment_id):
        try:
            assignment = TrainingAssignment.objects.get(id=assignment_id)
        except TrainingAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=404)

        serializer = TrainingAssignmentSerializer(assignment, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Assignment updated", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)

class TrainingAssignmentSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, assignment_id):
        try:
            assignment = TrainingAssignment.objects.get(id=assignment_id)
            assignment.is_completed = True  # Soft delete by marking completed
            assignment.save()
            return Response({"msg": "Assignment marked completed (soft deleted)"}, status=200)
        except TrainingAssignment.DoesNotExist:
            return Response({"error": "Assignment not found"}, status=404)


class TrainingLogUpdateView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def put(self, request, log_id):
        try:
            log = TrainingLog.objects.get(id=log_id)
        except TrainingLog.DoesNotExist:
            return Response({"error": "Log not found"}, status=404)

        serializer = TrainingLogSerializer(log, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"msg": "Log updated", "data": serializer.data}, status=200)
        return Response(serializer.errors, status=400)


class TrainingLogSoftDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUserCustom]
    def delete(self, request, log_id):
        try:
            log = TrainingLog.objects.get(id=log_id)
            log.status = "cancelled"  # Soft delete by setting a flag
            log.save()
            return Response({"msg": "Log cancelled (soft deleted)"}, status=status.HTTP_200_OK)
        except TrainingLog.DoesNotExist:
            return Response({"error": "Log not found"}, status=status.HTTP_404_NOT_FOUND)