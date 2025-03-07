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


class Search_Internships(APIView):
    serializer_class = InternshipSerializers

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Search Internships", operation_summary="Search Internships by passing ?title=''&location=''")
    def get(self, request, *args, **kwargs):
        title = request.query_params.get('title', None)
        location = request.query_params.get('location', None)
        
        internships = Internship.objects.all()
        if title:
            internships = internships.filter(title__icontains=title) | internships.filter(skills_required__icontains=title) | internships.filter(company__company_name__icontains=title)
        if location:
            internships = internships.filter(location__icontains=location)
            
        serializer = self.serializer_class(internships, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    

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
    serializer_class = Add_ApplicationSerializer
    parser_classes = (MultiPartParser, FormParser)
 
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="Api of Apply for Internship", operation_summary="Apply for Internship")
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            student = Student.objects.get(user=request.user)
            internship = serializer.validated_data['internship']
            
            if Application.objects.filter(student=student, internship=internship).exists():
                return Response({"message": "You have already applied for this internship."}, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.validated_data['student'] = Student.objects.get(user=request.user)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class Student_Applications(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get all applications of student", operation_summary="Get all applications of student")
    def get(self, request, *args, **kwargs):
        applications = Application.objects.filter(student__user=request.user)

        if not applications:
            return Response({"message": "No applications found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = Applied_Serializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class Applicationsby_status(APIView):
    permission_classes = [IsAuthenticated, IsStudent]

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get applications of student by Status", operation_summary="Get applications of student by Status = Pending,Shortlisted,Rejected,Selected")
    def get(self, request, stat):
        applications = Application.objects.filter(student__user=request.user, status=stat).order_by('-updated_at')

        if not applications:
            return Response({"message": "No applications found for this user."}, status=status.HTTP_404_NOT_FOUND)

        serializer = Applied_Serializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)