from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import BasePermission
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from .models import *
from core_app.models import *
from core_app.serializers import *
from .serializers import *

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