from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from .serializers import *
# Create your views here.

class RegisterOrganization(APIView):
    serializer_classes = OrgUserModelSerializer

    @swagger_auto_schema(tags=['Organization APIs'], request_body=serializer_classes, operation_description="API for Organization Registration", operation_summary="API for Organization Registration")
    def post(self, request, *args, **kwargs):
        if 'role' not in request.data or not request.data['role']:
            request.data['role'] = 'Organization'
        
        serializer = self.serializer_classes(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetOrgProfile(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = OrgUserModelSerializer

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="get organization data to profile",operation_summary="get organization data to profile"
                        )
    
    def get(self,request):
        user = request.user
        serializer = self.serializers_classes(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddIntern(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = InternshipSerializers

    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Add Internship to display Students",operation_summary="Add Internship to display Students",
                        request_body=serializers_classes
                        )

    def post(self,request):
        if request.method=='POST':
            data=request.data
            serialziser=self.serializers_classes(data=data)
            if serialziser.is_valid():
                serialziser.save()
                return Response(serialziser.data,status=status.HTTP_201_CREATED)
            else:
                return Response(serialziser.errors,status=status.HTTP_400_BAD_REQUEST)
            

class UpdateIntern(APIView):
    permission_classes = [IsAuthenticated]
    serializers_classes = InternshipSerializers


    @swagger_auto_schema(tags=['Organization APIs'],operation_description="Update Internship by organization",operation_summary="Update Internship by organization",
                        request_body=serializers_classes
                        )
    def put(self, request, intern_id):
        # Get the data from the request
        intern_data = request.data
        
        try:
            # Get the existing Internship object by intern_id
            intern_obj = Internship.objects.get(id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_class(data=intern_data, instance=intern_obj)
        
        if serializer.is_valid():
            serializer.save()  # Save the updated data
            return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  # Return validation errors


class GetInternData(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = InternshipSerializers

    def get(self,request,intern_id):
        try:
            # Get the existing Internship object by intern_id
            intern_obj = Internship.objects.get(id=intern_id)
        except Internship.DoesNotExist:
            return Response({"detail": "Internship not found."}, status=status.HTTP_404_NOT_FOUND)
        
        # Pass the object to the serializer to update it
        serializer = self.serializer_class(intern_obj)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    


class ShowInternship(APIView):
    permission_classes=[IsAuthenticated]
    serializer_classes = InternshipSerializers

    def get(self,request):
        intern_queryset = Internship.objects.all()
        # Pass the  queryset to the serializer to update it
        serializer = self.serializer_class(intern_queryset,many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)  # Return the updated data
    



