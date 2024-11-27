from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from drf_yasg.utils import swagger_auto_schema

from .serializers import *
# Create your views here.


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