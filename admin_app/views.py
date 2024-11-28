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
from organization_app.serializers import InternshipSerializers


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
    

class AllOrganization(APIView):
    serializer_classes = AllOrganizationSerializers
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show organization all data",operation_summary="show organization all data")
    def get(self,request):
        try:
            organ_all = Organization.objects.all()
        except Organization.DoesNotExist:
            return Response({"detail": "eror in fetch all organization"}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_classes(organ_all,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    

class InternshipsByOrgan(APIView):
    serializer_classes = InternshipSerializers
    permission_classes=[IsAuthenticated]

    @swagger_auto_schema(tags=['Admin APIs'],operation_description="show internship all data",operation_summary="show internship all data")
    def get(self,request,organ_id):
        try:
            organ_all = Internship.objects.filter(company_id=organ_id)
        except Internship.DoesNotExist:
            return Response({"detail": "eror in fetch all Internship"}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_classes(organ_all,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data

        
