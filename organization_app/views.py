from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework import status,permissions


from drf_yasg.utils import swagger_auto_schema

from .serializers import *
from student_app.serializers import *
from student_app.models import Student

from admin_app.models import *
from admin_app.serializers import *

# Create your views here.

class DistrictList(APIView):
    serializer_classes = DistrictSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All District List",operation_summary="All District List",
                        )

    def get(self,request):
        if request.method == 'GET':
            data = District.objects.all()
            serializer = self.serializer_classes(data,many=True) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class TalukaList(APIView):
    serializer_classes = TalukaSerializer
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All Taluka List",operation_summary="All Taluka List by District id",
    )

    def get(self,request,district_id):
        if request.method == 'GET':
            data = Taluka.objects.filter(district_id=district_id)
            serializer = self.serializer_classes(data,many=True) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class RegisterOrganization(APIView):
    serializer_class = OrgUserModelSerializer

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_class, operation_description="API for Organization Registration", operation_summary="API for Organization Registration")
    def post(self, request, *args, **kwargs):
        if 'role' not in request.data or not request.data['role']:
            request.data['role'] = 'Organization'
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IsOrg(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Organization"


class GetOrgProfile(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = OrgUserModelSerializer
    serializer_class1 = UpdateOrganizationSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="get organization data to profile",operation_summary="get organization data to profile")
    def get(self,request):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_class1, operation_description="Organization api for Edit Profile", operation_summary="Organization api for Edit Profile")
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class1(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Add_Internship(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = InternshipSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="API For Add Internship By Organisation",operation_summary="API for Add Internship By Organisation", request_body=serializer_class)
    def post(self,request):
        try:
            org = Organization.objects.get(user=request.user)
        except Organization.DoesNotExist:
            return Response({"error": "Organization not found for this user."}, status=status.HTTP_404_NOT_FOUND)
        
        data=request.data
        data['company'] = org.id
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            
class GetInternData(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="One Internship data show organization",operation_summary="One Internship data show organization")
    def get(self, request, intern_id):
        try:
            intern_obj = Internship.objects.get(intern_id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(intern_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    

class Update_Internship(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = InternshipSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Update Internship by organization",operation_summary="Update Internship by organization", request_body=serializer_class)
    def put(self, request, intern_id):
        intern_data = request.data
        
        try:
            intern_obj = Internship.objects.get(intern_id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(data=intern_data, instance=intern_obj, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class Org_GetInternships(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = InternshipSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All Internships data show organization",operation_summary="All Internships data show organization")
    def get(self, request, *args, **kwargs):        
        organisation = Organization.objects.get(user=request.user)
        internships = Internship.objects.filter(company=organisation.id)
        serializer = self.serializer_class(internships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class DeleteIntern(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Delete Internships data show organization",operation_summary="Delete Internships data")
    
    def delete(self,request,intern_id):
        try:
            # Get the existing Internship object by intern_id encrepted
            intern_obj = Internship.objects.get(intern_id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship id not found."}, status=status.HTTP_404_NOT_FOUND)
        
        intern_obj.delete()
        return Response({"success": "Internship deleted successfully."}, status=status.HTTP_200_OK)  # Return the updated data
    

class OrganizationAllApps(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ShowAllApplications


    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All Internships data show organization",operation_summary="All Internships data show organization")
    def get(self,request,intern_id):
        intern_obj=Internship.objects.get(intern_id=intern_id)
        apps_data = Application.objects.filter(internship_id=intern_obj.id)
        # Pass the  queryset to the serializer to update it
        serializer = self.serializer_class(apps_data,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    

class UpdateAppsStatus(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = AppUpdateSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="update status for application by organization",operation_summary="update status for application by organization"
                         ,request_body=serializer_class)
    
    def put(self,request):
        intern_id = request.data.get('internship')
        student_id = request.data.get('student')
    
        try:
            app_data = Application.objects.get(internship_id=intern_id, student_id=student_id)
        except Application.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)

   
        serializer = self.serializer_class(app_data, data=request.data, partial=True)  # partial=True allows partial updates
    
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
        
        user = Organization.objects.get(user= request.user)
        print(user.org_id)

        response_data= {"org_app_total":org_app_total,"Pending_app":Pending_app,"Selected_app":Selected_app,"Shortlisted_app":Shortlisted_app
                        ,"Rejected_app":Rejected_app}
        
        return Response(response_data,status=status.HTTP_200_OK)


class Add_MonthReport(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = MonthlyReportSerializer

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_class, operation_description="API for Adding Month Report to selected student", operation_summary="Add Month Report to Selected Student")
    def post(self, request):
        try:
            app_obj = Application.objects.get(id=request.data.get('application'))
        except Application.DoesNotExist:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if app_obj.status == 'Selected':
            serializer = self.serializer_class(data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        else:
            return Response({"detail": "Application not selected."}, status=status.HTTP_400_BAD_REQUEST)


class MonthReportby_student(APIView):
    permission_classes=[IsAuthenticated]
    serializer_class = MonthlyReportSerializer

    @swagger_auto_schema(tags=['Organization APIs'], operation_description="API for Get Report by Student", operation_summary="Get Report By Student")
    def get(self, request, stud_id, *args, **kwargs):
        reports = MonthlyReport.objects.filter(application__student__id = stud_id)
        serializer = self.serializer_class(reports, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


class SelectedStudent(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = SelectedStudentSerializer

    @swagger_auto_schema(tags=['Organization Selected-Student'], request_body=serializer_classes ,operation_description="Save Selected Student API", operation_summary="Save Selected Student API")

    def post(self,request):
        selected_query=request.data

        serializer=self.serializer_classes(data=selected_query)
        if serializer.is_valid():
            serializer.save()
            return Response({"success":"selected student status saved"},status=status.HTTP_201_CREATED)
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)
    
class GetAllSelected(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = SelectedStudentSerializer

    @swagger_auto_schema(tags=['Organization Selected-Student'],operation_description="All Selected Student API by organization", operation_summary="All Selected Student API by organization")
    def get(self,request):
        try:
            organization = Organization.objects.get(user=request.user)
       
            internships = Internship.objects.filter(company=organization)

            applications = Application.objects.filter(internship__in=internships)

            # Get selected students who have been linked to these applications
            selected_students = SelectedStudentModel.objects.filter(application__in=applications)

            # Serialize the selected students data
            serializer = AdminSelectedStudentSerializer(selected_students, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Organization.DoesNotExist:
            return Response({"organizations data not found"},status=status.HTTP_400_BAD_REQUEST)
        
    


class GetOneSelected(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = SelectedStudentSerializer


    @swagger_auto_schema(tags=['Organization Selected-Student'],operation_description="One Selected Student API by organization", operation_summary="One Selected Student API by organization")
    def get(self,request,selected_id):
        # Get selected students who have been linked to these applications
        selected_students = SelectedStudentModel.objects.get(id=selected_id)

        # Serialize the selected students data
        serializer = SelectedStudentSerializer(selected_students)
        return Response(serializer.data, status=status.HTTP_200_OK)




    


class UpdateSelectedStudent(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = SelectedStudentSerializer
    @swagger_auto_schema(tags=['Organization Selected-Student'], request_body=serializer_classes , operation_description="Update Selected Student API", operation_summary="Update Selected Student API")
    
    def put(self, request, selected_id):
        try:
            # Find the student by primary key
            selected_student = SelectedStudentModel.objects.get(id=selected_id)
        except SelectedStudent.DoesNotExist:
            return Response({"detail": "Selected student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the instance with the data from the request
        serializer = self.serializer_classes(selected_student, data=request.data, partial=False)

        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response({"success": "Selected student status updated."}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeleteSelectedStudent(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = SelectedStudentSerializer

    @swagger_auto_schema(tags=['Organization Selected-Student'],operation_description="Delete Selected Student API", operation_summary="Delete Selected Student API")
    def delete(self, request, selected_id):
        try:
            # Find the student by primary key
            selected_student = SelectedStudentModel.objects.get(id=selected_id)
        except SelectedStudent.DoesNotExist:
            return Response({"detail": "Selected student not found."}, status=status.HTTP_404_NOT_FOUND)

        # Delete the selected student
        selected_student.delete()
        return Response({"success": "Selected student deleted."}, status=status.HTTP_200_OK)
    

class AllSelectedApps(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_classes = ShowSelectedApplications

    @swagger_auto_schema(tags=['Organization Selected-List'],operation_description="show selected student API", operation_summary="show selected student API")
    def get(self,request):
        all_interns=Internship.objects.filter(company__user=request.user)
        intern_apps = Application.objects.filter(internship__company__user=request.user,status='Selected')
        serializer = self.serializer_classes(intern_apps,many=True)
        return Response(serializer.data,status=status.HTTP_200_OK)




    

