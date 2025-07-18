from django.db.models import Q

from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema

from .serializers import LoginSerializer,UserSerialiazer
from .models import *

import math

# class Registration(APIView):
#     serializer_class = UserSerialiazer
#     permission_classes = [permissions.AllowAny]
    
#     @swagger_auto_schema(tags=['Config APIs'], operation_description="API for Registration", operation_summary="Registration API",request_body=serializer_class)
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

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
            
            role = UserModel.objects.get(email=user).role
            
            response = {
                'access': str(access_token), 
                'refresh': str(refresh), 
                'role': role, 
                'name':f"{user.first_name} {user.last_name}"
            }
            
            if role == "Student":
                response["is_education_filled"] = user.student.is_education_filled
            
            
            # Return the tokens
            return Response(response,status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class CustomPaginator(PageNumberPagination):
    page_size = 10  # default
    page_query_param = 'page'
    page_size_query_param = 'size'

    def get_paginated_response(self, data):
        total_pages = math.ceil(self.page.paginator.count / self.page_size)
        
        return Response({
            'count': self.page.paginator.count,
            'current_page':self.page.number,
            'total_pages': total_pages,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })
        
        
class CustomSearchFilter(SearchFilter):
    def filter_queryset(self, request, queryset, view):
        search_fields = getattr(view, 'search_fields', None)
        search_term = self.get_search_terms(request)

        if not search_fields or not search_term:
            return queryset

        conditions = Q()
        for term in search_term:
            or_query = Q()
            for field in search_fields:
                or_query |= Q(**{f"{field}__icontains": term})
            conditions &= or_query

        return queryset.filter(conditions).distinct()
