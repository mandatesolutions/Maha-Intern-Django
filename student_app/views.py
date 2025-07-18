from django.shortcuts import render
from django.http import Http404

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