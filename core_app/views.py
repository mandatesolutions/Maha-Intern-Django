from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework import status,permissions
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import *

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .serializers import *
from .models import *
from .utils import get_room_name

import math

# class Registration(APIView):
#     serializer_class = UserSerialiazer
#     permission_classes = [permissions.AllowAny]
    
#     @swagger_auto_schema(tags=['Config APIs'], operation_description='API for Registration', operation_summary='Registration API',request_body=serializer_class)
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

    @swagger_auto_schema(tags=['Core APIs'], operation_description='Api for Login user', operation_summary='Api for Login user',request_body=serializer_class)
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
                'name':f'{user.first_name} {user.last_name}'
            }
            
            if role == 'Student':
                student = user.student
                if student.is_blocked:
                    return Response(
                        {'details': f'Student - {student.user.first_name} {student.user.last_name} is blocked by admin'}, 
                        status=status.HTTP_403_FORBIDDEN
                    )
                response['is_education_filled'] = student.is_education_filled
                
            if role == 'Organization':
                organization = user.organization
                if not organization.is_approved:
                    return Response({'details': f'Organization - {organization.company_name} is not approved by admin'}, status=status.HTTP_403_FORBIDDEN)
            
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
                or_query |= Q(**{f'{field}__icontains': term})
            conditions &= or_query

        return queryset.filter(conditions).distinct()

class FeedbackQuestionListView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['Core APIs'],
        operation_description='Get Feedback Questions',
        operation_summary='Get Feedback Questions',
        manual_parameters=[
            openapi.Parameter(
                'feedback_for',
                openapi.IN_PATH,
                description='Feedback target (student or organization)',
                type=openapi.TYPE_STRING,
                enum=['student', 'organization']
            )
        ]
    )
    def get(self, request, feedback_for):
        if feedback_for not in ['student', 'organization']:
            return Response({'detail': 'Invalid feedback target.'}, status=status.HTTP_400_BAD_REQUEST)
        questions = FeedbackQuestion.objects.filter(feedback_for=feedback_for)
        return Response([{'id': q.question_id, 'question': q.question_text} for q in questions])

class GetAllNotifications(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer
    
    @swagger_auto_schema(tags=['Core APIs'], operation_description='Get All Notifications',operation_summary='Get All Notifications',)
    def get(self, request):
        notifications = Notification.objects.filter(user=request.user)
        serializer = self.serializer_class(notifications, many=True)
        return Response(
            {
                'notifications': serializer.data,
                'unread_count': notifications.filter(is_read=False).count()   
            }, 
            status=status.HTTP_200_OK
        )
        
class MarkNotificationAsRead(APIView):
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        tags=['Core APIs'], 
        operation_description='Mark Notification As Read',
        operation_summary='Mark Notification As Read',
        manual_parameters=[
            openapi.Parameter(
                'notification_id',
                openapi.IN_PATH,
                description='Notification ID',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def patch(self, request, notification_id):
        notification = get_object_or_404(Notification, id=notification_id, user=request.user)
        notification.is_read = True
        notification.save()
        return Response({'detail': 'Notification marked as read.'}, status=status.HTTP_200_OK)
    
class Get_ChatHistory(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ChatMessageSerializer
    
    def get_queryset(self):
        sender_id = self.request.user.id
        receiver_id = self.kwargs['receiver_id']
        room_name = get_room_name(sender_id, receiver_id)
        messages = ChatMessage.objects.filter(room_name=room_name)
        return messages
    

    @swagger_auto_schema(
        tags=['Core APIs'], 
        operation_description="Get Chat History",
        operation_summary="Get Chat History",
        manual_parameters=[
            openapi.Parameter(
                'receiver_id',
                openapi.IN_PATH,
                description='Receiver ID',
                type=openapi.TYPE_INTEGER
            )
        ]
    )
    def get(self, request, receiver_id):
        return super().get(request, receiver_id)