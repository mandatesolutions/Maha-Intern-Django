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

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get 10 Internships", operation_summary="Get Get 10 Internships")
    def get(self, request, *args, **kwargs):
        internships = Internship.objects.all().order_by('-id')[:10]
        serializer = self.serializer_class(internships, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class Student_Dashboard(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    
    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Student Dashboard", operation_summary="Student Dashboard")
    def get(self, request, *args, **kwargs):
        applied = Application.objects.filter(student__user=request.user)
        appliedcount = applied.count()
        shortlisted = applied.filter(status='Shortlisted').count()
        selected = applied.filter(status='Selected').count()
        rejected = applied.filter(status='Rejected').count()
        
        return Response({'appliedcount': appliedcount, 'shortlisted': shortlisted, 'selected': selected, 'rejected': rejected,}, status=status.HTTP_200_OK)
    
    
class Student_ProfileDetail(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = UserModelSerializer

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
    serializer_class = InternshipSerializer
    
    def get_object(self, uid):
        try:
            return Internship.objects.get(intern_id=uid)
        except Internship.DoesNotExist:
            raise NotFound("Scholarship not found.")

    @swagger_auto_schema(tags=['Student APIs'], operation_description="API for Get Internship by uid", operation_summary="Get Internship by id")
    def get(self, request, uid, format=None):
        internship = self.get_object(uid)
        serializer = self.serializer_class(internship)
        return Response(serializer.data, status=status.HTTP_200_OK)


class Student_Internshipapply(APIView):
    permission_classes = [IsAuthenticated, IsStudent]
    serializer_class = ApplicationSerializer
    
    parser_classes = (MultiPartParser, FormParser)
    @swagger_auto_schema(tags=['Student APIs'], request_body=serializer_class, operation_description="Api of Apply for Internship", operation_summary="Apply for Internship")
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # Set the student to the logged-in user
            # serializer.validated_data['student'] = request.user
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

        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)