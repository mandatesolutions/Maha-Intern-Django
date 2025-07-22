from django.shortcuts import render
from django.db.utils import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, BasePermission
from rest_framework.generics import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import *
from .serializers import *

from student_app.serializers import *
from student_app.models import Student

from admin_app.models import *
from admin_app.serializers import *

from core_app.serializers import *
from core_app.views import CustomSearchFilter, CustomPaginator

# Create your views here.

class DistrictList(APIView):
    serializer_classes = DistrictSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="All District List",operation_summary="All District List",
                        )

    def get(self,request):
        if request.method == 'GET':
            data = District.objects.all()
            serializer = self.serializer_classes(data,many=True) 
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class TalukaList(APIView):
    serializer_classes = TalukaSerializer

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
        
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.validated_data['company'] = org
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
    

class OrganizationAllApps(ListAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = ShowAllApplications
    
    def get_queryset(self):
        intern_id = self.kwargs['intern_id']
        status = self.request.query_params.get('status')
        
        appilcation = Application.objects.filter(internship__intern_id=intern_id)
        
        if status:
            appilcation = appilcation.filter(status=status)
            
        return appilcation


    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="All Internships data show organization",
        operation_summary="All Internships data show organization",
        manual_parameters=[
            openapi.Parameter(
                "status",
                openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                enum=["pending", "shortlisted", "rejected", "selected","accepted","declined"],
            )
        ]
    )
    def get(self,request,intern_id):
        return super().get(request, intern_id)
    

class UpdateAppsStatus(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="update status for application by organization",
        operation_summary="update status for application by organization",
        manual_parameters=[
            openapi.Parameter(
                "app_status",
                openapi.IN_PATH,
                type=openapi.TYPE_STRING,
                enum=["shortlisted", "selected", "rejected"],
            )
        ]
    )
    def patch(self,request,app_id,app_status):
        
        if app_status not in ["shortlisted", "rejected", "selected"]:
            return Response({"detail": "Invalid status. Status must be 'shortlisted', 'selected', or 'rejected'."}, status=status.HTTP_400_BAD_REQUEST)
        
        application = Application.objects.filter(app_id=app_id).first()
        if not application:
            return Response({"detail": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        old_status = application.status
        application.status = app_status
        application.save()
        ApplicationStatusHistory.objects.create(application=application, old_status=old_status, new_status=app_status)
        Notification.objects.create(
            title="Application Status Updated",
            message=f"Your application status for {application.internship.title} has been updated to {app_status}.",
            user=application.student.user
        )
        
        if app_status == "selected":
            SelectedStudentModel.objects.create(application=application)
            
        return Response({"success": "Application status updated successfully."}, status=status.HTTP_200_OK)        
        

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


class ListMonthlyReview(ListAPIView):
    permission_classes=[IsAuthenticated, IsOrg]
    serializer_class = MonthlyReviewOrganizationToStudentSerializer
    
    def get_queryset(self):
        stud_id = self.request.query_params.get('stud_id')
        monthly_reviews = MonthlyReviewOrganizationToStudent.objects.filter(organization__user=self.request.user)
        if stud_id:
            monthly_reviews = monthly_reviews.filter(student__stud_id=stud_id) 
        return monthly_reviews
    
    @swagger_auto_schema(
        tags=['Organization APIs'], 
        operation_description="API for Get Month Report", 
        operation_summary="Get Month Report",
        manual_parameters=[
            openapi.Parameter("stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CreateMonthlyReview(APIView):
    permission_classes=[IsAuthenticated, IsOrg]
    serializer_class = MonthlyReviewOrganizationToStudentSerializer

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_class, operation_description="API for Adding Month Report to selected student", operation_summary="Add Month Report to Selected Student")
    def post(self, request, stud_id):
        student = Student.objects.filter(stud_id=stud_id).first()
        if not student:
            return Response({"detail": "Student not found."}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.validated_data['student'] = student
            serializer.validated_data['organization'] = request.user.organization
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MonthlyReviewView(RetrieveDestroyAPIView):
    permission_classes=[IsAuthenticated, IsOrg]
    serializer_class = MonthlyReviewOrganizationToStudentSerializer
    lookup_field = 'review_id'
    
    def get_queryset(self):
        return MonthlyReviewOrganizationToStudent.objects.filter(organization__user=self.request.user)
    
    @swagger_auto_schema(tags=['Organization APIs'], operation_description="API for Get Month Report", operation_summary="Get Month Report")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Organization APIs'], operation_description="API for Delete Month Report", operation_summary="Delete Month Report")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Organization APIs'], operation_description="API for Update Month Report", operation_summary="Update Month Report")
    def put(self, request, review_id):
        review_id = MonthlyReviewOrganizationToStudent.objects.filter(review_id=review_id).first()
        
        if not review_id:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(review_id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
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
        selected_students = SelectedStudentModel.objects.get(selected_student_id=selected_id)

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
            selected_student = SelectedStudentModel.objects.get(selected_student_id=selected_id)
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
            selected_student = SelectedStudentModel.objects.get(selected_student_id=selected_id)
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

class Org_InterviewDetailsView(APIView):
    permission_classes = [IsAuthenticated,IsOrg]
    serializer_class = InterviewDetailsSerializer
    
    def get_application(self, app_id):
        return get_object_or_404(Application, app_id=app_id)

    def get_interview(self, application):
        return InterviewDetails.objects.filter(application=application).first()
    
    @swagger_auto_schema(tags=['Organization APIs'],request_body=serializer_class,operation_description="Add Interview Details API", operation_summary="Add Interview Details API")
    def post(self, request, app_id):
        application = Application.objects.filter(app_id=app_id).first()
        
        if application.status != 'selected':
            return Response({"detail": "Application is not selected."}, status=status.HTTP_400_BAD_REQUEST)

        if self.get_interview(application):
            return Response({"detail": "Interview details already exist for this application."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            serializer.save(application=application)
            Notification.objects.create(
                title="Interview Scheduled",
                message=f"Your interview has been scheduled for {application.internship.title}.",
                user=application.student.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Get Interview Details API", operation_summary="Get Interview Details API")
    def get(self, request, app_id):
        application = self.get_application(app_id)
        interview = self.get_interview(application)
        
        if not interview:
            return Response({"detail": "Interview details not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(interview)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(tags=['Organization APIs'],request_body=serializer_class,operation_description="Update Interview Details API", operation_summary="Update Interview Details API")
    def put(self, request, app_id):
        application = self.get_application(app_id)
        interview = self.get_interview(application)
        
        if not interview:
            return Response({"detail": "Interview details not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(interview, data=request.data)
        
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Org_OfferDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = OfferDetailsSerializer

    def get_application(self, app_id):
        return get_object_or_404(Application, app_id=app_id)

    def get_offer(self, application):
        return OfferDetails.objects.filter(application=application).first()

    @swagger_auto_schema(
        tags=['Organization APIs'],
        request_body=serializer_class,
        operation_description="Add Offer Details API",
        operation_summary="Add Offer Details API (use FormData)"
    )
    def post(self, request, app_id):
        application = self.get_application(app_id)

        if application.status != 'selected':
            return Response({"detail": "Application is not selected."}, status=status.HTTP_400_BAD_REQUEST)

        if self.get_offer(application):
            return Response({"detail": "Offer details already exist for this application."}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(application=application)
            Notification.objects.create(
                title="Offer added",
                message=f"Your Offer has been added, for {application.internship.title}.",
                user=application.student.user
            )
            selected_student = SelectedStudentModel.objects.get(application=application)
            selected_student.joining_date = serializer.validated_data['joining_date']
            selected_student.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get Offer Details API",
        operation_summary="Get Offer Details API"
    )
    def get(self, request, app_id):
        application = self.get_application(app_id)
        offer = self.get_offer(application)
        
        if not offer:
            return Response({"detail": "Offer details not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(offer)
        return Response(serializer.data)

    @swagger_auto_schema(
        tags=['Organization APIs'],
        request_body=serializer_class,
        operation_description="Update Offer Details API",
        operation_summary="Update Offer Details API (User FormData)"
    )
    def put(self, request, app_id):
        application = self.get_application(app_id)
        offer = self.get_offer(application)
        
        if not offer:
            return Response({"detail": "Offer details not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(offer, data=request.data)
        if serializer.is_valid():
            serializer.save()
            Notification.objects.create(
                title="Offer details Updated",
                message=f"Your Offer details has been updated, for {application.internship.title}.",
                user=application.student.user
            )
            
            selected_student = SelectedStudentModel.objects.get(application=application)
            selected_student.joining_date = serializer.validated_data['joining_date']
            selected_student.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Organization Reviewing Student
# 1. Organization Reviews Student
class OrganizationReviewStudent(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = ReviewSerializer  # For response

    @swagger_auto_schema(
        tags=['Organization APIs'],
        request_body=serializer_class,
        operation_description="Organization post review on student",
        operation_summary="Post Review on student"
    )
    def post(self, request, stud_id):
        try:
            student = Student.objects.get(stud_id=stud_id)
            organization = request.user.organization
        except Student.DoesNotExist:
            return Response({'detail': 'Student not found'}, status=404)

        data = {
            'reviewer_type': 'organization',
            'reviewer_organization': organization,
            'reviewed_student': student,
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment')
        }

        review = Review.objects.create(**data)
        serializer = self.serializer_class(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 2. Organization Given reviews by self
class OrganizationGivenReviews(ListAPIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = Organization_GivenReviewsSerializer

    def get_queryset(self):
        return Review.objects.filter(reviewer_organization=self.request.user.organization)

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get reviews given by organization",
        operation_summary="Organization's given reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# 3. Organization Received reviews from Student
class OrganizationReceivedReviews(ListAPIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = Student_GivenReviewsSerializer

    def get_queryset(self):
        return Review.objects.filter(reviewed_organization=self.request.user.organization)

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get reviews received by organization",
        operation_summary="Organization's received reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# 4. Organization sees Student reviews
class OrganizationViewStudentReviews(ListAPIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = Organization_GivenReviewsSerializer

    def get_queryset(self):
        stud_id = self.kwargs.get('stud_id')
        if stud_id:
            try:
                student = Student.objects.get(stud_id=stud_id)
                return Review.objects.filter(reviewed_student=student)
            except Student.DoesNotExist:
                return Review.objects.none()
        return Review.objects.filter(reviewed_student__isnull=False)

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get reviews of a student",
        operation_summary="Student reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# Feedback Reviews
# 1. Organization gives feedback on Student
class OrganizationGiveFeedbackToStudent(APIView):
    permission_classes = [IsAuthenticated, IsOrg]
    serializer_class = FeedbackResponseSerializer

    @swagger_auto_schema(
        tags=['Organization APIs'],
        request_body=serializer_class,
        operation_description="Give feedback to student",
        operation_summary="Organization gives feedback to student"
    )
    def post(self, request, stud_id):
        serializer = self.serializer_class(
            data=request.data,
            context={'request': request, 'recipient_id': stud_id, 'feedback_type': 'organisation_to_student'}
        )
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response(
                    {"detail": "Feedback has already been submitted for this student for this month."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Organization sees feedbacks given by them
class OrganizationFeedbacksGiven(APIView):
    permission_classes = [IsAuthenticated, IsOrg]

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get feedbacks given by organization",
        operation_summary="Organization's given feedbacks"
    )
    def get(self, request):
        org = request.user.organization
        feedbacks = FeedbackResponse.objects.filter(sender_organization=org, feedback_type='organisation_to_student')
        serializer = FeedbackResponseSerializer(feedbacks, many=True)
        return Response(serializer.data)

# 3. Organization sees feedbacks received from Students
class FeedbacksGivenOnOrganization(APIView):
    permission_classes = [IsAuthenticated, IsOrg]

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get feedbacks given on organization",
        operation_summary="Feedbacks received by organization"
    )
    def get(self, request):
        org = request.user.organization
        feedbacks = FeedbackResponse.objects.filter(recipient_organization=org, feedback_type='student_to_organisation')
        serializer = FeedbackResponseSerializer(feedbacks, many=True)
        return Response(serializer.data)
    
# 4. Organization sees feedbacks of Student(s)
class FeedbacksOfStudentForOrganization(APIView):
    permission_classes = [IsAuthenticated, IsOrg]

    @swagger_auto_schema(
        tags=['Organization APIs'],
        operation_description="Get feedbacks of student(s)",
        operation_summary="Feedbacks given to student(s)"
    )
    def get(self, request, stud_id=None):
        if stud_id:
            try:
                student = Student.objects.get(stud_id=stud_id)
                feedbacks = FeedbackResponse.objects.filter(recipient_student=student, feedback_type='organisation_to_student')
            except Student.DoesNotExist:
                return Response({'detail': 'Student not found'}, status=404)
        else:
            feedbacks = FeedbackResponse.objects.filter(feedback_type='organisation_to_student')

        serializer = FeedbackResponseSerializer(feedbacks, many=True)
        return Response(serializer.data)

class RecievedMonthlyReviewView(ListAPIView):
    permission_classes=[IsAuthenticated, IsOrg]
    serializer_class = MonthlyReviewStudentToOrganizationSerializer
    
    def get_queryset(self):
        stud_id = self.request.query_params.get('stud_id')
        monthly_reviews = MonthlyReviewStudentToOrganization.objects.filter(organization__user=self.request.user)
        if stud_id:    
            monthly_reviews = monthly_reviews.filter(student__stud_id=stud_id)
        return monthly_reviews
    
    @swagger_auto_schema(
        tags=['Organization APIs'], 
        operation_description="API for Get Recieved Monthly Report from student", 
        operation_summary="Get Recieved Monthly Report",
        manual_parameters=[
            openapi.Parameter("stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class Org_SearchStudents(ListAPIView):
    permission_classes=[IsAuthenticated, IsOrg]
    serializer_class = SearchStudentSerializer
    queryset = Student.objects.filter(is_blocked=False)
    pagination_class = CustomPaginator
    filter_backends = [CustomSearchFilter]
    search_fields = [
        'stud_id', 'user__first_name', 'user__last_name', 'user__email',
        'district','taluka','gender','last_course','university','profile','language','skills'
    ]
    
    @swagger_auto_schema(
        tags=['Organization APIs'], 
        operation_description="API for serach students", 
        operation_summary="Get All Students",
        manual_parameters=[
            openapi.Parameter(
                "search", openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                description="Search by [ 'stud_id', 'first_name', 'last_name', 'email', 'district','taluka','gender','last_course','university','profile','language','skills' ]")
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
        