from . import views
from django.urls import path, include

urlpatterns = [
    # path('registration/', views.Registration.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    
    path('notifications/', views.GetAllNotifications.as_view(), name='notifications'),
    path('notification/<int:notification_id>', views.MarkNotificationAsRead.as_view(), name='notification'),
    
    path('feedback-questions/<str:feedback_for>', views.FeedbackQuestionListView.as_view(), name='notifications'),
    
    path('chat-history/<int:receiver_id>', views.Get_ChatHistory.as_view(), name='chat-history'),
]