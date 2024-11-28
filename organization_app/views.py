from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from student_app.serializers import UserModelSerializer
from student_app.models import Student
# Create your views here.

class RegisterOrganization(APIView):
    serializer_classes = OrgUserModelSerializer

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_classes, operation_description="API for Organization Registration", operation_summary="API for Organization Registration")
    def post(self, request, *args, **kwargs):
        if 'role' not in request.data or not request.data['role']:
            request.data['role'] = 'Organization'
        
        serializer = self.serializer_classes(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetOrgProfile(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = OrgUserModelSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="get organization data to profile",operation_summary="get organization data to profile"
                        )
    
    def get(self,request):
        user = request.user
        serializer = self.serializers_classes(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddIntern(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Add Internship to display Students",operation_summary="Add Internship to display Students",
                        request_body=serializers_classes
                        )

    def post(self,request):
        if request.method=='POST':
            data=request.data
            serialziser=self.serializers_classes(data=data)
            if serialziser.is_valid():
                serialziser.save()
                return Response(serialziser.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serialziser.errors,status=status.HTTP_400_BAD_REQUEST)
            

class UpdateIntern(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = InternshipSerializers


    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Update Internship by organization",operation_summary="Update Internship by organization",
                        request_body=serializers_classes
                        )
    def put(self, request, intern_id):
        # Get the data from the request
        intern_data = request.data
        
        try:
            # Get the existing Internship object by intern_id
            intern_obj = Internship.objects.get(id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializers_classes(data=intern_data, instance=intern_obj)
        
        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors


class GetInternData(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="One Internship data show organization",operation_summary="One Internship data show organization")
    def get(self,request,intern_id):
        try:
            # Get the existing Internship object by intern_id
            intern_obj = Internship.objects.get(id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_classes(intern_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    


class ShowInternship(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = InternshipSerializers


    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All Internships data show organization",operation_summary="All Internships data show organization")
    def get(self,request,organ_id):
        intern_queryset = Internship.objects.filter(company_id=organ_id)
        # Pass the  queryset to the serializer to update it
        serializer = self.serializer_classes(intern_queryset,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data




class DeleteIntern(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Delete Internships data show organization",operation_summary="Delete Internships data")
    
    def delete(self,request,intern_id):
        try:
            # Get the existing Internship object by intern_id
            intern_obj = Internship.objects.get(id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship id not found."}, status=status.HTTP_404_NOT_FOUND)
        
        intern_obj.delete()
        return Response({"success": "Internship deleted successfully."}, status=status.HTTP_200_OK)  # Return the updated data
    

class OrganizationAllApps(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = ApplicationSerializer


    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All Internships data show organization",operation_summary="All Internships data show organization")
    def get(self,request,intern_id):
        apps_data = Application.objects.filter(internship_id=intern_id)
        # Pass the  queryset to the serializer to update it
        serializer = self.serializer_classes(apps_data,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    

class UpdateAppsStatus(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = AppUpdateSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="update status for application by organization",operation_summary="update status for application by organization"
                         ,request_body=serializer_classes)
    
    def put(self,request):
        intern_id = request.data.get('internship')
        student_id = request.data.get('student')
    
        try:
            app_data = Application.objects.get(internship_id=intern_id, student_id=student_id)
        except Application.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

   
        serializer = self.serializer_classes(app_data, data=request.data, partial=True)  # partial=True allows partial updates
    
        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class GetStudentProfile(APIView):
    serializer_class = UserModelSerializer
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Organization APIs'], operation_description="for Get profile of student", operation_summary="for Get profile of student")
    def get(self, request, student_id):
        try:
            # Fetch the Student object by ID
            stud_obj = Student.objects.get(id=student_id)
            print("student_obj",stud_obj)
            # Serialize the Student object (which includes the nested User data)
            serializer = self.serializer_class(stud_obj.user)
            
            # Return the serialized data as response
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Student.DoesNotExist:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        

class OrgDashCounter(APIView):
    serializer_class = UserModelSerializer
    # permission_classes=[IsAuthenticated] 

    @swagger_auto_schema(tags=['Organization APIs'], operation_description="for Get organization counter", operation_summary="for Get organization counter")
    def get(self, request):
        all_interns=Internship.objects.filter(company__user=request.user)
        intern_apps = Application.objects.filter(internship__company__user=request.user)
        org_app_total = intern_apps.count()
        Pending_app=intern_apps.filter(status='Pending').count()
        Selected_app=intern_apps.filter(status='Selected').count()
        Shortlisted_app=intern_apps.filter(status='Shortlisted').count()
        Rejected_app=intern_apps.filter(status='Rejected').count()
        

        response_data= {"org_app_total":org_app_total,"Pending_app":Pending_app,"Selected_app":Selected_app,"Shortlisted_app":Shortlisted_app
                        ,"Rejected_app":Rejected_app}
        
        return Response(response_data,status=status.HTTP_200_OK)








