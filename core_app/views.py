from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from drf_yasg.utils import swagger_auto_schema
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import LoginSerializer,UserSerialiazer
from .models import *
# Create your views here.


class Registration(APIView):
    serializer_class = UserSerialiazer
    permission_classes = [permissions.AllowAny]
    
    @swagger_auto_schema(tags=['Config APIs'], operation_description="API for Registration", operation_summary="Registration API",request_body=serializer_class)
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

# login api user

class LoginView(APIView):
    permission_classes = [permissions.AllowAny]  
    serializer_class = LoginSerializer

    @swagger_auto_schema(tags=['Config APIs'], operation_description="Api for Login user", operation_summary="Api for Login user",request_body=serializer_class)
    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            # Get the authenticated user from the serializer
            user = serializer.validated_data['user']

            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            # Return the tokens
            return Response({"success":"Login Successfully.",'refresh': str(refresh),'access': str(access_token)},status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    