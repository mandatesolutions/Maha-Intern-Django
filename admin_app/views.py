from django.shortcuts import render
from django.http import Http404
from django.db.models import Count, Q, Avg
from django.utils.timezone import now
from django.http import HttpResponse

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
from .serializers import *

from core_app.models import *
from core_app.serializers import *
from core_app.views import CustomSearchFilter, CustomPaginator

from organization_app.models import *
from organization_app.serializers import *

from student_app.serializers import MonthlyReviewStudentToOrganizationSerializer

import os
import mimetypes

# Create your views here.
class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Admin'


class AdminDashboardCounter(APIView):
    serializer_classes = ApplicationSerializer
    permission_classes=[IsAuthenticated,IsAdmin]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description='show applications and Internships counter',operation_summary='show applications and Internships counter')
    def get(self,request):
        organ_data = Organization.objects.all()
        all_interns=Internship.objects.all()
        intern_apps = Application.objects.all()
        org_app_total = intern_apps.count()
        Pending_app=intern_apps.filter(status='Pending').count()
        Selected_app=intern_apps.filter(status='Selected').count()
        Shortlisted_app=intern_apps.filter(status='Shortlisted').count()
        Rejected_app=intern_apps.filter(status='Rejected').count()
        

        response_data= {'All_Organization':organ_data.count(),'All_internship':all_interns.count(),'Organization_apps_total':org_app_total,'Pending_app':Pending_app,'Selected_app':Selected_app,'Shortlisted_app':Shortlisted_app
                        ,'Rejected_app':Rejected_app}
        
        return Response(response_data,status=status.HTTP_200_OK)

class Admin_DashboardOverview(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='Admin Dahsboard Overview',operation_summary='Get Admin Dashboard Overview')
    def get(self, request):
        jobs_count = Internship.objects.count()
        organizations_count = Organization.objects.count()
        students_count = Student.objects.count()
        active_internships = Internship.objects.filter(last_date_of_apply__gte=now().date()).count()
        placed_students = Student.objects.filter(student_applications__status='accepted').count()
        total_applications = Application.objects.count()
        total_interviews = InterviewDetails.objects.count()

        # Top recruiters by students placed & job posts
        top_organizations = (
            Organization.objects.annotate(
                total_jobs=Count('company_internships', distinct=True),
                students_placed=Count(
                    'company_internships__internship_applications',
                    filter=Q(company_internships__internship_applications__status='accepted'),
                    distinct=True
                ),
                average_rating=Avg('organization_received_reviews__rating')  
            )
            .order_by('-students_placed', '-average_rating')[:10]
        )

        top_recruiters = [
            {
                'name': organization.company_name,
                'email': organization.user.email,
                'total_jobs_posted': organization.total_jobs,
                'students_placed': organization.students_placed,
                'average_rating': round(organization.average_rating or 0, 2)
            }
            for organization in top_organizations
        ]

        data = {
            'jobs_count': jobs_count,
            'organizations_count': organizations_count,
            'students_count': students_count,
            'total_applications': total_applications,
            'total_interviews': total_interviews,
            'active_internships': active_internships,
            'placed_students': placed_students,
            'top_recruiters': top_recruiters
        }

        return Response(data, status=status.HTTP_200_OK)    

# Student APIs
class Admin_StudentsListView(ListAPIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    serializer_class = Allstudent_Serializer
    queryset = Student.objects.all()
    pagination_class = CustomPaginator
    filter_backends = [CustomSearchFilter]
    search_fields = [
        'user__first_name','user__last_name','user__email','district','taluka','gender','last_course','university','profile','language','skills'
    ]

    @swagger_auto_schema(tags=['Admin APIs'], operation_description='API for Get all Students', operation_summary='Get all Students')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class Admin_RetrieveStudentView(RetrieveAPIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    serializer_class = Allstudent_Serializer
    queryset = Student.objects.all()
    lookup_field = 'stud_id'
    
    @swagger_auto_schema(tags=['Admin APIs'], operation_description='API for Get Student', operation_summary='Get Student')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class Admin_BlockUnBlockStudentView(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='API for block or unblock student',
        operation_summary='Block or Unblock Student',
        manual_parameters=[
            openapi.Parameter('stud_id', openapi.IN_PATH, type=openapi.TYPE_STRING, ),
            openapi.Parameter("stud_status", openapi.IN_PATH, type=openapi.TYPE_STRING, enum=['block', 'unblock']),
        ]
    )
    def patch(self, request, stud_id, stud_status):
        student = get_object_or_404(Student, stud_id=stud_id)
        student.is_blocked = True if stud_status == 'block' else False
        student.save()
        return Response({'details': f'Student {'blocked' if stud_status == 'block' else 'unblocked'} successfully.'}, status=status.HTTP_200_OK)
    
class Admin_StudentResumesListView(ListAPIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    serializer_class = StudentResumesSerializer
    queryset = Student.objects.exclude(resume__isnull=True).exclude(resume__exact='')
    pagination_class = CustomPaginator
    filter_backends = [CustomSearchFilter]
    search_fields = ['user__first_name','user__last_name','user__email','district','taluka','gender','last_course','university','profile','language','skills']
    
    @swagger_auto_schema(tags=['Admin APIs'], operation_description='API for Get Student Resumes', operation_summary='Get Student Resumes')
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)
    
class Admin_DownloadStudentResume(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description="API to Download Student Resume", operation_summary="Download Student Resume")
    def get(self, request, stud_id):
        student = get_object_or_404(Student, stud_id=stud_id)
        resume_file = student.resume
        if not resume_file or not os.path.isfile(resume_file.path):
            return Response({"detail": "Resume File Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        file_path = resume_file.path
        file_name = resume_file.name

        # Guess the content type
        content_type, _ = mimetypes.guess_type(file_path)
        content_type = content_type or 'application/octet-stream'

        # Read and return the file
        with open(file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_name)}"'
            return response
class Admin_ForwardStudentProfileToOrganization(APIView):
    permission_classes = [IsAuthenticated,IsAdmin]
    serializer_class = ForwardStudentProfileSerializer
    
    @swagger_auto_schema(tags=['Admin APIs'],request_body=serializer_class,operation_description="API to Forward Student Profile", operation_summary="Forward Student Profile")
    def post(self, request, *args, **kwargs):
        org_id = request.data.get('org_id')
        organization = get_object_or_404(Organization, org_id=org_id)
        Notification.objects.create(
            title="Student Profile Forwarded",
            message=f"Student Profile has been forwarded by Admin",
            redirect_url=request.data.get('redirect_url'),
            user=organization.user
        )
        return Response({"message": "Student Profile forwarded successfully"},status=status.HTTP_200_OK)

# Organization APIs
class Admin_OrganizationListCreateView(ListAPIView):
    serializer_class = AllOrganizationSerializers
    permission_classes=[IsAuthenticated, IsAdmin]
    queryset = Organization.objects.all()
    pagination_class = CustomPaginator
    filter_backends = [CustomSearchFilter]
    search_fields = ['company_name','disctrict','taluka','reprsentative_name','industry_type']
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='Get all the Organization',operation_summary='All Organization')
    def get(self,request):
        return super().get(request)
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='create organization data',request_body=serializer_class,operation_summary='create organization ')
    def post(self,request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['user']['role'] = 'Organization'
            serializer.validated_data['is_approved'] = True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)    
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class Admin_RetrieveUpdateDestroyOrganizationView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AllOrganizationSerializers
    queryset = Organization.objects.all()
    lookup_field = 'org_id'
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='get organization ',operation_summary='get organization ')
    def get(self, request, org_id):
        return super().get(request, org_id)
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='update organization ',request_body=serializer_class,operation_summary='update organization ')
    def put(self, request, org_id):
        organization = self.get_object()
        user_data = request.data.pop('user')
        serializer = OrganizationSerializers(organization, data=request.data)
        if serializer.is_valid():
            user = organization.user
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.email = user_data['email']
            user.mobile = user_data['mobile']
            user.save()
            serializer.save()
            
            response = {
                **serializer.data,
                'user': user_data
            }
            return Response(response, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='delete organization',operation_summary='delete organization ')
    def delete(self, request, org_id):
        organization = self.get_object()
        organization.delete()
        organization.user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class Admin_ApproveBlockOrganizationView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='approve or block organization',
        operation_summary='approve or block organization ',
        manual_parameters=[
            openapi.Parameter(
                'org_status', openapi.IN_PATH, type=openapi.TYPE_STRING, description='Approve or block the organization', enum=['approve', 'block']
            )
        ]
    )
    def patch(self, request, org_id, org_status):
        organization = get_object_or_404(Organization, org_id=org_id)
        organization.is_approved = True if org_status == 'approve' else False
        organization.save()
        return Response({'details':f'{organization.company_name} is {'approved' if org_status == 'approve' else 'blocked'}'} ,status=status.HTTP_200_OK)

# Internship APIs 
class Admin_InternshipListView(ListAPIView):
    serializer_class = AdminShowInternshipSerializers
    permission_classes=[IsAuthenticated, IsAdmin]
    pagination_class = CustomPaginator
    
    def get_queryset(self):
        org_id = self.request.query_params.get('org_id')
        is_approved = self.request.query_params.get('is_approved')
        
        internships = Internship.objects.all()
        if org_id:
            internships = internships.filter(company__org_id=org_id)
        if is_approved:
            is_approved = is_approved.lower() in ['true', '1']
            internships = internships.filter(is_approved=is_approved)
        
        return internships

    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get all the Internships or by organization',
        operation_summary='Get Internships or by organization',
        manual_parameters=[
            openapi.Parameter(
                'org_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by organization ID',
            ),
            openapi.Parameter(
                'is_approved', openapi.IN_QUERY, type=openapi.TYPE_BOOLEAN, description='Filter by approval status',
            ),
        ]
    )
    def get(self,request):
        return super().get(request)
    
class Admin_InternshipCreateView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminShowInternshipSerializers
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='create internship on behalf of organization ',request_body=serializer_class,operation_summary='create internship ')
    def post(self, request, org_id):
        organization = get_object_or_404(Organization, org_id=org_id)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.validated_data['company'] = organization
            serializer.validated_data['is_approved'] = True
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class Admin_InternshipRetrieveUpdateDeleteView(RetrieveDestroyAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = AdminShowInternshipSerializers
    queryset = Internship.objects.all()
    lookup_field = 'intern_id'
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='get internship ',operation_summary='get internship ')
    def get(self, request, intern_id):
        return super().get(request, intern_id)
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='update internship ',request_body=serializer_class,operation_summary='update internship ')
    def put(self, request, intern_id):
        internship = get_object_or_404(Internship, intern_id=intern_id)
        serializer = self.serializer_class(internship, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(tags=['Admin APIs'],operation_description='delete internship',operation_summary='delete internship ')
    def delete(self, request, intern_id):
        return super().delete(request, intern_id)
    
class Admin_ApproveBlockInternship(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='approve or reject internship',
        operation_summary='approve or reject internship ',
        manual_parameters=[
            openapi.Parameter(
                'intern_status', openapi.IN_PATH, type=openapi.TYPE_STRING, description='Approve or reject the internship', enum=['approve', 'reject']
            )
        ]
    )
    def patch(self, request, intern_id, intern_status):
        internship = get_object_or_404(Internship, intern_id=intern_id)
        internship.is_approved = True if intern_status == 'approve' else False
        internship.save()
        return Response({'details':f'{internship.title} is {'approved' if intern_status == 'approve' else 'rejected'}'} ,status=status.HTTP_200_OK)
    
    
# Internship Applications
class Admin_ApplicationsListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ApplicationDetailedSerializer
    pagination_class = CustomPaginator

    def get_queryset(self):
        intern_id = self.request.query_params.get('intern_id')
        stud_id = self.request.query_params.get('stud_id')
        org_id = self.request.query_params.get('org_id')
        status = self.request.query_params.get('status')
        
        applications = Application.objects.all()
        if intern_id:
            applications = applications.filter(internship__intern_id=intern_id)
        if stud_id:
            applications = applications.filter(student__stud_id=stud_id)
        if org_id:
            applications = applications.filter(internship__company__org_id=org_id)
        if status:
            applications = applications.filter(status=status)
        
        return applications
    
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get all the Applications or by internship or student or organization or status',
        operation_summary='Get Applications or by internship or student or organization or status',
        manual_parameters=[
            openapi.Parameter(
                'intern_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by internship ID',
            ),
            openapi.Parameter(
                'stud_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by student ID',
            ),
            openapi.Parameter(
                'org_id', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by organization ID',
            ),
            openapi.Parameter(
                'status', openapi.IN_QUERY, type=openapi.TYPE_STRING, description='Filter by application status', enum=['pending', 'shortlisted', 'rejected', 'selected','accepted','rejected'],
            )
        ]
    )
    def get(self,request):
        return super().get(request)
    
class Admin_RetrieveApplication(RetrieveAPIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = ApplicationDetailedSerializer
    queryset = Application.objects.all()
    lookup_field = 'app_id'
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get a specific Application by ID',
        operation_summary='Get a specific Application by ID'
    )
    def get(self, request, app_id):
        return super().get(request, app_id)
    
class Admin_InterviewDetailsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = InterviewDetailsSerializer
    
    def get_queryset(self):
        app_id = self.kwargs['app_id']
        return get_object_or_404(InterviewDetails, application__app_id=app_id)
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get a specific Interview by ID',
        operation_summary='Get a specific Interview by ID'
    )
    def get(self, request, app_id):
        interview = self.get_queryset()
        serializer = self.serializer_class(interview)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='create Interview details',
        operation_summary='create Interview details',
        request_body=serializer_class
    )
    def post(self, request, app_id):
        application = get_object_or_404(Application, app_id=app_id)
        
        if application.status != 'shortlisted':
            return Response({"detail": "Application is not shortlisted."}, status=status.HTTP_400_BAD_REQUEST)
        
        if InterviewDetails.objects.filter(application=application).exists():
            return Response({"detail": "Interview details already exist for this application."}, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(application=application)
            Notification.objects.create(
                title="Interview Scheduled",
                message=f"Your interview has been scheduled for {application.internship.title}.",
                user=application.student.user
            )
            Notification.objects.create(
                title="Interview Scheduled",
                message=f"Interview has been scheduled for {application.internship.title} by Admin.",
                user=application.internship.company.user
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='update Interview details',
        operation_summary='update Interview details',
        request_body=serializer_class
    )
    def put(self, request, app_id):
        interview = self.get_queryset()
        serializer = self.serializer_class(interview, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            Notification.objects.create(
                title="Interview Details Updated",
                message=f"Your interview details have been updated for {interview.application.internship.title}.",
                user=interview.application.student.user
            )
            Notification.objects.create(
                title="Interview Details Updated",
                message=f"Interview details have been updated for {interview.application.internship.title} by Admin.",
                user=interview.application.internship.company.user
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class AppsByIntern(APIView):
    serializer_classes = ShowInternApplicationSerializer
    permission_classes=[IsAuthenticated,IsAdmin]


    @swagger_auto_schema(tags=['Admin APIs'],operation_description='show applications by Internships data',operation_summary='show applications by Internships data')
    def get(self,request,intern_id):
        queryset = Application.objects.filter(internship_id=intern_id)

        serializer=self.serializer_classes(queryset,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    

    


class LatestStudent(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description='Latest registered students at dashboard',operation_summary='Latest registered students at dashboard')

    def get(self,request):
        
        raw_query = '''SELECT u.id,st.id as Student_id,u.first_name,u.last_name,u.email,st.adhar_number,u.date_joined as Registered_Date FROM MahaIntern_DB.Student as st
        Left Join MahaIntern_DB.UserModel as u on st.user_id = u.id
        WHERE st.id IS NOT NULL ORDER BY u.date_joined DESC LIMIT 10;'''

        student_query=Student.objects.raw(raw_query)

        student_data = [
            {   
                'User_id': row.id,
                'Student_id': row.Student_id,
                'student_name': row.first_name+row.last_name,
                'email': row.email,
                'adhar_number': row.adhar_number,
                'Registered_Date': row.Registered_Date,
            }
            for row in student_query
        ]

        return Response(student_data,status=status.HTTP_200_OK)


# Reports, Reviews, Feedbacks APIs
class Admin_ListMonthlyReportofStudent(ListAPIView):
    serializer_class = MonthlyReviewOrganizationToStudentSerializer
    permission_classes=[IsAuthenticated, IsAdmin]

    def get_queryset(self):
        monthly_reviews = MonthlyReviewOrganizationToStudent.objects.all()
        
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        stud_id = self.request.query_params.get('stud_id')
        org_id = self.request.query_params.get('org_id')
        
        if year:
            monthly_reviews = monthly_reviews.filter(year=year)
        if month:
            monthly_reviews = monthly_reviews.filter(month=month)
        if stud_id:
            monthly_reviews = monthly_reviews.filter(student__stud_id=stud_id)
        if org_id:
            monthly_reviews = monthly_reviews.filter(organization__org_id=org_id)
            
        return monthly_reviews

    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get Monthly report of students or by student id',
        operation_summary='Get Monthly report of students or by student id',
        manual_parameters=[
            openapi.Parameter(
                "stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by reported student ID",
            ),
            openapi.Parameter(
                "org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by reporter organization ID",
            ),
            openapi.Parameter(
                "year", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by year",
            ),
            openapi.Parameter(
                "month", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by month",
            ),
        ]
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)
    
class Admin_ListMonthlyReportofOrganization(ListAPIView):
    serializer_class = MonthlyReviewStudentToOrganizationSerializer
    permission_classes=[IsAuthenticated, IsAdmin]

    def get_queryset(self):
        monthly_reviews = MonthlyReviewStudentToOrganization.objects.all()
        
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        stud_id = self.request.query_params.get('stud_id')
        org_id = self.request.query_params.get('org_id')
        
        if year:
            monthly_reviews = monthly_reviews.filter(year=year)
        if month:
            monthly_reviews = monthly_reviews.filter(month=month)
        if stud_id:
            monthly_reviews = monthly_reviews.filter(student__stud_id=stud_id)
        if org_id:
            monthly_reviews = monthly_reviews.filter(organization__org_id=org_id)
            
        return monthly_reviews
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get Monthly report of organizations or by organization id',
        operation_summary='Get Monthly report of organizations or by organization id',
        manual_parameters=[
            openapi.Parameter(
                "org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by reported organization ID",
            ),
            openapi.Parameter(
                "stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by reporter student ID",
            ),
            openapi.Parameter(
                "year", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by year",
            ),
            openapi.Parameter(
                "month", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by month",
            ),
        ]
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)
    
class Admin_ReviewsListView(ListAPIView):
    serializer_class = AdminAllReviewsSerializer
    permission_classes=[IsAuthenticated, IsAdmin]
    queryset = Review.objects.all()
    pagination_class = CustomPaginator

    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get all the Reviews or by student or organization',
        operation_summary='Get all the Reviews or by student or organization',
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)
    
class Admin_FeedbacksOfStudent(ListAPIView):
    serializer_class = FeedbackResponseSerializer
    permission_classes=[IsAuthenticated, IsAdmin]
    pagination_class = CustomPaginator
    
    def get_queryset(self):
        feedback_responses = FeedbackResponse.objects.filter(feedback_type='organisation_to_student')
        
        stud_id = self.request.query_params.get('stud_id')
        org_id = self.request.query_params.get('org_id')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        
        if year:
            feedback_responses = feedback_responses.filter(year=year)
        if month:
            feedback_responses = feedback_responses.filter(month=month)
        if stud_id:
            feedback_responses = feedback_responses.filter(recipient_student__stud_id=stud_id)
        if org_id:
            feedback_responses = feedback_responses.filter(sender_organization__org_id=org_id)
        
        return feedback_responses
        

    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get all the Feedbacks of students or by student id',
        operation_summary='Get all the Feedbacks of students or by student id',
        manual_parameters=[
            openapi.Parameter(
                "stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by recipient student ID",
            ),
            openapi.Parameter(
                "org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by sender organization ID",
            ),
            openapi.Parameter(
                "year", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by year",
            ),
            openapi.Parameter(
                "month", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by month",
            ),
        ]
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)

class Admin_FeedbacksOfOrganization(ListAPIView):
    serializer_class = FeedbackResponseSerializer
    permission_classes=[IsAuthenticated, IsAdmin]
    pagination_class = CustomPaginator
    
    def get_queryset(self):
        feedback_responses = FeedbackResponse.objects.filter(feedback_type='student_to_organisation')
        
        stud_id = self.request.query_params.get('stud_id')
        org_id = self.request.query_params.get('org_id')
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        
        if year:
            feedback_responses = feedback_responses.filter(year=year)
        if month:
            feedback_responses = feedback_responses.filter(month=month)
        if stud_id:
            feedback_responses = feedback_responses.filter(sender_student__stud_id=stud_id)
        if org_id:
            feedback_responses = feedback_responses.filter(recipient_organization__org_id=org_id)
        
        return feedback_responses
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Get all the Feedbacks of organizations or by organization id',
        operation_summary='Get all the Feedbacks of organizations or by organization id',
        manual_parameters=[
            openapi.Parameter(
                "stud_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by sender student ID",
            ),
            openapi.Parameter(
                "org_id", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by recipient organization ID",
            ),
            openapi.Parameter(
                "year", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by year",
            ),
            openapi.Parameter(
                "month", openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description="Filter by month",
            ),
        ]
    )
    def get(self,request,*args,**kwargs):
        return super().get(request,*args,**kwargs)

class GetJoinedStudents(APIView):
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin Joined-Student'],operation_description='Get Joined Students API by organization', operation_summary='Joined Students API by organization')
    def get(self,request,organ_uid):
        organization = Organization.objects.get(org_id=organ_uid)
        internships = Internship.objects.filter(company=organization)
        applications = Application.objects.filter(internship__in=internships)
        selected_students = SelectedStudentModel.objects.filter(application__in=applications)

        serializer = AdminSelectedStudentSerializer(selected_students, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class OrgSelectedApps(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminShowSelectedApplications

    @swagger_auto_schema(tags=['Admin Joined-Student'],operation_description='Get Selected Students API by organization', operation_summary='Selected Students API by organization')
    def get(self,request,organ_uid):
        organization = Organization.objects.get(org_id=organ_uid)
        internships = Internship.objects.filter(company=organization)
        applications = Application.objects.filter(internship__in=internships,status='Selected')

        serializer=self.serializer_class(applications,many=True)

        return Response(serializer.data,status=status.HTTP_200_OK)
    
class Admin_FeedbackQuestionsView(APIView):
    permission_classes = [IsAuthenticated, IsAdmin]
    serializer_class = FeedbackQuestionsSerializer
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='show feedback questions',
        operation_summary='show feedback questions',
        manual_parameters=[
            openapi.Parameter(
                'feedback_for',
                openapi.IN_PATH,
                description='Feedback target (student or organization)',
                type=openapi.TYPE_STRING,
                enum=['student', 'organization']
            )
        ]
    )
    def get(self, request, feedback_for):
        
        if feedback_for not in ['student', 'organization']:
            return Response({'detail': 'Invalid feedback target.'}, status=status.HTTP_400_BAD_REQUEST)
        
        feedback_questions = FeedbackQuestion.objects.filter(feedback_for=feedback_for)
        serializer = self.serializer_class(feedback_questions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
    @swagger_auto_schema(
        tags=['Admin APIs'],
        operation_description='Create feedback questions (accepts list of strings)',
        operation_summary='Create feedback questions',
        manual_parameters=[
            openapi.Parameter(
                'feedback_for',
                openapi.IN_PATH,
                description='Feedback target (student or organization)',
                type=openapi.TYPE_STRING,
                enum=['student', 'organization']
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_ARRAY,
            items=openapi.Items(type=openapi.TYPE_STRING),
            description='List of question texts'
        )
    )
    def post(self, request, feedback_for):
        if feedback_for not in ['student', 'organization']:
            return Response({'detail': 'Invalid feedback target.'}, status=status.HTTP_400_BAD_REQUEST)

        questions = request.data
        if not isinstance(questions, list) or not all(isinstance(q, str) for q in questions):
            return Response({'detail': 'Request body must be a list of strings.'}, status=status.HTTP_400_BAD_REQUEST)

        response = []
        for q in questions:
            obj = FeedbackQuestion.objects.create(question_text=q, feedback_for=feedback_for)
            response.append({
                'question_id': obj.question_id,
                'question_text': obj.question_text,
                'feedback_for': obj.feedback_for
            })

        return Response(response, status=status.HTTP_201_CREATED)

