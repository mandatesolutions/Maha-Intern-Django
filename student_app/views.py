from django.shortcuts import render
from django.http import Http404
from django.db.utils import IntegrityError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.exceptions import NotFound
from rest_framework.generics import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import *
from core_app.models import *
from core_app.serializers import *
from core_app.views import CustomSearchFilter, CustomPaginator
from organization_app.models import *
from .serializers import *
from organization_app.serializers import *

from datetime import date


# Create your views here.

class IsStudent(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == "Student"


class Student_Registration(APIView):
    serializer_class = UserModelSerializer
    
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="API for Student Registration", operation_summary="Student Registration API")
    def post(self, request, *args, **kwargs):
        if 'role' not in request.data or not request.data['role']:
            request.data['role'] = 'Student'
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Student_GetInternships(APIView):
    serializer_class = InternshipSerializers

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get 10 Internships", operation_summary="Get 10 Internships")
    def get(self, request, *args, **kwargs):
        internships = Internship.objects.all().order_by('-id')[:9]
        serializer = self.serializer_class(internships, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class Search_Internships(ListAPIView):
    serializer_class = InternshipSerializers
    queryset = Internship.objects.all()
    pagination_class = CustomPaginator
    filter_backends = [CustomSearchFilter]
    search_fields = [ 
        'intern_type', 'title', 'description', 'no_of_openings', 'stipend_type', 'stipend_amount', 'location', 'duration', 'skills_required', 'start_date', 'last_date_of_apply', 'perks', 'qualification_in', 'specialisation_in', 'terms', 'company__company_name'
    ]

    @swagger_auto_schema(
        tags=['Student APIs'], 
        operation_description="API for Search Internships", 
        operation_summary="Search Internships",
        manual_parameters=[
            openapi.Parameter(
                'search', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                description="Search by [ 'intern_type', 'title', 'description', 'no_of_openings', 'stipend_type', 'stipend_amount', 'location', 'duration', 'skills_required', 'start_date', 'last_date_of_apply', 'perks', 'qualification_in', 'specialisation_in', 'terms', 'company__company_name' ]"
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    

class Student_Dashboard(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Student Dashboard", operation_summary="Student Dashboard")
    def get(self, request, *args, **kwargs):
        applied = Application.objects.filter(student__user=request.user)
        appliedcount = applied.count()
        pending = applied.filter(status='Pending').count()
        shortlisted = applied.filter(status='Shortlisted').count()
        selected = applied.filter(status='Selected').count()
        rejected = applied.filter(status='Rejected').count()
        
        return Response({'appliedcount': appliedcount, 'pending': pending, 'shortlisted': shortlisted, 'selected': selected, 'rejected': rejected,}, status=status.HTTP_200_OK)
    
    
class Student_ProfileDetail(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = Update_UserModelSerializer

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get Profile", operation_summary="Get Profile")
    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="API for Edit Profile", operation_summary="Edit Profile")
    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Student_InternshipDetail(APIView):
    serializer_class = InternshipSerializers
    
    def get_object(self, uid):
        try:
            return Internship.objects.get(intern_id=uid)
        except Internship.DoesNotExist:
            raise NotFound("Internship not found.")

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get Internship by uid", operation_summary="Get Internship by id")
    def get(self, request, uid, format=None):
        internship = self.get_object(uid)
        serializer = self.serializer_class(internship, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class Student_Internshipapply(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
 
    @swagger_auto_schema(tags=['Student APIs'], operation_description="Api of Apply for Internship", operation_summary="Apply for Internship")
    def post(self, request, intern_id):
        internship = Internship.objects.filter(intern_id=intern_id).first()
        student = request.user.student
        if internship:
            
            if internship.last_date_of_apply  < date.today():
                return Response({"message": "Internship application deadline has passed."}, status=status.HTTP_400_BAD_REQUEST)
            
            if Application.objects.filter(internship__intern_id=intern_id, student=student).exists():
                return Response({"message": "You have already applied for this internship."}, status=status.HTTP_400_BAD_REQUEST)
            
            application = Application.objects.create(internship=internship, student=student)
            ApplicationStatusHistory.objects.create(application=application, old_status='pending', new_status='pending')
            
            return Response({"message": "Internship applied successfully."}, status=status.HTTP_201_CREATED)
        else:
            return Response({"message": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
class Student_Applications(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ApplicationDetailsSerializer
    
    def get_queryset(self):
        student = self.request.user.student
        
        applications = Application.objects.select_related(
            'student__user', 'internship__company'
        ).prefetch_related(
            'status_history', 'application_interview', 'application_offer'
        ).filter(student=student).order_by('-updated_at')
        
        app_status = self.request.query_params.get('status')
        if app_status:
            applications = applications.filter(status=app_status)
            
        return applications
        
    @swagger_auto_schema(
        tags=['Student APIs'], 
        operation_description="API for Get all applications of student", 
        operation_summary="Get all applications of student",
        manual_parameters=[
            openapi.Parameter(
                'status',
                openapi.IN_QUERY,
                description='Filter applications by status',
                type=openapi.TYPE_STRING,
                enum=['pending', 'shortlisted', 'rejected', 'selected'],
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class Student_EducationView(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = EducationSerializer
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get Education", operation_summary="Get Education")
    def get(self, request):
        educations = Education.objects.filter(student__user=request.user)
        serializer = self.serializer_class(educations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="API for Add Education", operation_summary="Add Education")
    def post(self, request):
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.validated_data['student'] = request.user.student
            serializer.save()
            
            # Update the student's is_education_filled field to True
            student = request.user.student
            student.is_education_filled = True
            student.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="API for Update Education", operation_summary="Update Education")
    def put(self, request):
        education = request.user.student.student_education
        serializer = self.serializer_class(education, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Student_AcceptDeclineOffer(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    
    @swagger_auto_schema(
        tags=['Student APIs'], 
        operation_description="API for Accept/Decline Offer", 
        operation_summary="Accept/Decline Offer",
        manual_parameters=[
            openapi.Parameter(
                'app_status',
                openapi.IN_PATH,
                description='Application Status',
                type=openapi.TYPE_STRING,
                enum=['accept', 'decline'],
                required=True,
            ),
        ]
    )
    def post(self, request, app_id, app_status):
        application = Application.objects.filter(app_id=app_id).first()
        old_status = application.status
        
        if not application:
            return Response({"message": "Application not found."}, status=status.HTTP_404_NOT_FOUND)
        
        if app_status not in ["accept", "decline"]:
            return Response({"message": "Invalid status. Status must be 'accept' or 'decline'."}, status=status.HTTP_400_BAD_REQUEST)
        
        if old_status != "selected":
            return Response({"message": "Application is not selected."}, status=status.HTTP_400_BAD_REQUEST)
        
        application.status = app_status
        application.save()
        
        if app_status == "accept":
            Notification.objects.create(
                title="Offer Accepted",
                message=f"Offer Accepted for {application.internship.title} by {application.student.user.first_name} {application.student.user.last_name}.",
                user=application.internship.company.user
            )
            selected_student = SelectedStudentModel.objects.get(application=application)
            selected_student.status = "Joined"
            selected_student.save()
        else:
            Notification.objects.create(
                title="Offer Declined",
                message=f"Offer Declined for {application.internship.title} by {application.student.user.first_name} {application.student.user.last_name}.",
                user=application.internship.company.user
            )
            
        ApplicationStatusHistory.objects.create(application=application, old_status=old_status, new_status=app_status)
        
        return Response(
            {"message": f"Application offer {"accepted" if app_status == "accept" else "declined"} successfully."}, 
            status=status.HTTP_200_OK
        )

# Student Reviewing Organization
# 1. Student reviews Organization    
class StudentReviewOrganization(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ReviewSerializer

    @swagger_auto_schema(
        tags=['Student APIs'],
        request_body=serializer_class,
        operation_description="Post review on Organization by Student",
        operation_summary="Student posts review on Organization",
    )
    def post(self, request, org_id):
        try:
            organization = Organization.objects.get(org_id=org_id)
            student = request.user.student
        except Organization.DoesNotExist:
            return Response({'detail': 'Organization not found'}, status=404)

        data = {
            'reviewer_type': 'student',
            'reviewer_student': student,
            'reviewed_organization': organization,
            'rating': request.data.get('rating'),
            'comment': request.data.get('comment')
        }

        review = Review.objects.create(**data)
        serializer = self.serializer_class(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

# 2. Student sees reviews given by self
class StudentGivenReviews(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = Student_GivenReviewsSerializer

    def get_queryset(self):
        return Review.objects.filter(reviewer_student=self.request.user.student)

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get reviews given by Student",
        operation_summary="Student's given reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# 3. Student sees reviews received
class StudentReceivedReviews(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(reviewed_student=self.request.user.student)

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get reviews received by Student",
        operation_summary="Student's received reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

# 4. Student sees reviews of an organization    
class OrganizationReviewsView(ListAPIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = Student_GivenReviewsSerializer

    def get_queryset(self):
        org_id = self.kwargs.get('org_id')
        if org_id:
            try:
                organization = Organization.objects.get(org_id=org_id)
                return Review.objects.filter(reviewed_organization=organization)
            except Organization.DoesNotExist:
                return Review.objects.none()
        return Review.objects.filter(reviewed_organization__isnull=False)

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get reviews of an organization",
        operation_summary="Organization reviews"
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
# Student Feedback Organization
# 1. Student gives feedback to student
class StudentGiveFeedback(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = FeedbackResponseSerializer

    @swagger_auto_schema(
        tags=['Student APIs'],
        request_body=serializer_class,
        operation_description="Post feedback to Organization by Student",
        operation_summary="Student gives feedback to Organization"
    )
    def post(self, request, org_id):
        data = request.data
        serializer = self.serializer_class(
            data=data,
            context={'request': request, 'recipient_id': org_id,'feedback_type': 'student_to_organisation'}
        )
        if serializer.is_valid():
            try:
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                return Response(
                    {"detail": "Feedback has already been submitted for this organization for this month."},
                    status=status.HTTP_400_BAD_REQUEST
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# 2. Student sees feedback given by self
class StudentFeedbacksGiven(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = FeedbackResponseSerializer

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get feedbacks given by Student",
        operation_summary="Student's given feedbacks"
    )
    def get(self, request):
        student = request.user.student
        feedbacks = FeedbackResponse.objects.filter(sender_student=student, feedback_type='student_to_organisation')
        serializer = self.serializer_class(feedbacks, many=True)
        return Response(serializer.data)

# 3. Student sees feedback received
class FeedbacksOnStudent(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = FeedbackResponseSerializer

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get feedbacks received by Student",
        operation_summary="Feedbacks received by Student"
    )
    def get(self, request):
        student = request.user.student
        feedbacks = FeedbackResponse.objects.filter(recipient_student=student, feedback_type='organisation_to_student')
        serializer = self.serializer_class(feedbacks, many=True)
        return Response(serializer.data)

# 4. Student sees feedback of an organization
class FeedbacksForOrganization(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FeedbackResponseSerializer

    @swagger_auto_schema(
        tags=['Student APIs'],
        operation_description="Get feedbacks for an Organization or all",
        operation_summary="Feedbacks for Organization(s)"
    )
    def get(self, request, org_id=None):
        if org_id:
            try:
                org = Organization.objects.get(org_id=org_id)
                feedbacks = FeedbackResponse.objects.filter(recipient_organization=org, feedback_type='student_to_organisation')
            except Organization.DoesNotExist:
                return Response({'detail': 'Organization not found'}, status=404)
        else:
            feedbacks = FeedbackResponse.objects.filter(feedback_type='student_to_organisation')

        serializer = self.serializer_class(feedbacks, many=True)
        return Response(serializer.data)

class ListMonthlyReview(ListAPIView):
    permission_classes=[IsAuthenticated, IsStudent]
    serializer_class = MonthlyReviewStudentToOrganizationSerializer
    
    def get_queryset(self):
        org_id = self.request.query_params.get('org_id')
        monthly_reviews = MonthlyReviewStudentToOrganization.objects.filter(student__user=self.request.user)
        if org_id:
            monthly_reviews = monthly_reviews.filter(organization__org_id=org_id) 
        return monthly_reviews
    
    @swagger_auto_schema(
        tags=['Student APIs'], 
        operation_description="API for Get Month Report", 
        operation_summary="Get Month Report",
        manual_parameters=[
            openapi.Parameter("org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

class CreateMonthlyReview(APIView):
    permission_classes=[IsAuthenticated, IsStudent]
    serializer_class = MonthlyReviewStudentToOrganizationSerializer

    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="API for Adding Month Report to selected student", operation_summary="Add Month Report to Selected Student")
    def post(self, request, org_id):
        organization = Organization.objects.filter(org_id=org_id).first()
        if not organization:
            return Response({"detail": "organization not found."}, status=status.HTTP_404_NOT_FOUND)
        data = request.data
        serializer = self.serializer_class(data=data)
        if serializer.is_valid():
            serializer.validated_data['student'] = request.user.student
            serializer.validated_data['organization'] = organization
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class MonthlyReviewView(RetrieveDestroyAPIView):
    permission_classes=[IsAuthenticated]
    serializer_class = MonthlyReviewStudentToOrganizationSerializer
    lookup_field = 'review_id'
    
    def get_queryset(self):
        return MonthlyReviewStudentToOrganization.objects.filter(student__user=self.request.user)
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get Month Report", operation_summary="Get Month Report")
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Delete Month Report", operation_summary="Delete Month Report")
    def delete(self, request, *args, **kwargs):
        return super().delete(request, *args, **kwargs)
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Update Month Report", operation_summary="Update Month Report")
    def put(self, request, review_id):
        review_id = MonthlyReviewStudentToOrganization.objects.filter(review_id=review_id).first()
        
        if not review_id:
            return Response({"detail": "Review not found."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.serializer_class(review_id, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
class RecievedMonthlyReviewView(ListAPIView):
    permission_classes=[IsAuthenticated, IsStudent]
    serializer_class = MonthlyReviewOrganizationToStudentSerializer
    
    def get_queryset(self):
        org_id = self.request.query_params.get('org_id')
        monthly_reviews = MonthlyReviewOrganizationToStudent.objects.filter(student__user=self.request.user)
        if org_id:    
            monthly_reviews = monthly_reviews.objects.filter(organization__org_id=org_id)
        return monthly_reviews
    
    @swagger_auto_schema(
        tags=['Student APIs'], 
        operation_description="API for Get Month Report", 
        operation_summary="Get Month Report",
        manual_parameters=[
            openapi.Parameter("org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING, )
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)