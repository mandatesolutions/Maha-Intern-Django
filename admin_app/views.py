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