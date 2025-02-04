from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound
from drf_yasg.utils import swagger_auto_schema
from .models import *
from core_app.models import *
from core_app.serializers import *
from organization_app.models import *
from .serializers import *
from organization_app.serializers import *


# Create your views here.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Admin"


class Admin_Allstudents(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Allstudent_Serializer

    @swagger_auto_schema(tags=['Admin APIs'], operation_description="API for Get all Students", operation_summary="Get all Students")
    def get(self, request, *args, **kwargs):
        students = Student.objects.all()
        serializer = self.serializer_class(students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class AllOrganization(APIView):
    serializer_classes = AllOrganizationSerializers
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show organization all data",operation_summary="show organization all data")
    def get(self,request):
        try:
            organ_all = Organization.objects.all()
        except Organization.DoesNotExist:
            return Response({"detail": "eror in fetch all organization"}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_classes(organ_all,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    

class InternshipsByOrgan(APIView):
    serializer_classes = AdminShowInternshipSerializers
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show internship all data",operation_summary="show internship all data")
    def get(self,request,organ_id):
        try:
            organ_obj=Organization.objects.get(org_id = organ_id)
            organ_all = Internship.objects.filter(company_id=organ_obj.id)
        except Internship.DoesNotExist:
            return Response({"detail": "eror in fetch all Internship"}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_classes(organ_all,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    


class AppsByIntern(APIView):
    serializer_classes = ShowInternApplicationSerializer
    permission_classes=[IsAuthenticated]


    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show applications by Internships data",operation_summary="show applications by Internships data")
    def get(self,request,intern_id):
        queryset = Application.objects.filter(internship_id=intern_id)

        serializer=self.serializer_classes(queryset,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    


class AdminDashboardCounter(APIView):
    serializer_classes = ApplicationSerializer
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show applications and Internships counter",operation_summary="show applications and Internships counter")
    def get(self,request):
        organ_data = Organization.objects.all()
        all_interns=Internship.objects.all()
        intern_apps = Application.objects.all()
        org_app_total = intern_apps.count()
        Pending_app=intern_apps.filter(status='Pending').count()
        Selected_app=intern_apps.filter(status='Selected').count()
        Shortlisted_app=intern_apps.filter(status='Shortlisted').count()
        Rejected_app=intern_apps.filter(status='Rejected').count()
        

        response_data= {"All_Organization":organ_data.count(),"All_internship":all_interns.count(),"Organization_apps_total":org_app_total,"Pending_app":Pending_app,"Selected_app":Selected_app,"Shortlisted_app":Shortlisted_app
                        ,"Rejected_app":Rejected_app}
        
        return Response(response_data,status=status.HTTP_200_OK)
    
class GetStudentInfo(APIView):
    serializer_classes = Allstudent_Serializer
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show student info for application",operation_summary="show student info for application")
    def get(self,request,student_id):
        try:
            stud_data = Student.objects.get(id = student_id)
        except Student.DoesNotExist:
            return Response({"error":"Student id not found"})
        
        serializer = self.serializer_classes(stud_data)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class GetOrganInfo(APIView):
    serializer_classes = AllOrganizationSerializers
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show organization info for application",operation_summary="show organization info for application")
    def get(self,request,organ_id):
        try:
            organ_data = Organization.objects.get(id = organ_id)
        except Organization.DoesNotExist:
            return Response({"error":"Organization id not found"})
        
        serializer = self.serializer_classes(organ_data)
        return Response(serializer.data,status=status.HTTP_200_OK)
    
class GetStudentReport(APIView):
    serializer_classes = MonthlyReportSerializer
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show organization info for application",operation_summary="show organization info for application")
    def get(self,request,student_id):
        try:
            report_data = MonthlyReport.objects.filter(application__student__stud_id = student_id)
        except MonthlyReport.DoesNotExist:
            return Response({"error":"student id not found"})
       
        serializer = self.serializer_classes(report_data,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)
    



class GetJoinedStudents(APIView):
    permission_classes=[IsAuthenticated]

    def get(self,request,organ_uid):
        organization = Organization.objects.get(org_id=organ_uid)
        internships = Internship.objects.filter(company=organization)
        applications = Application.objects.filter(internship__in=internships)
        selected_students = SelectedStudentModel.objects.filter(application__in=applications)

        serializer = AdminSelectedStudentSerializer(selected_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    








        
