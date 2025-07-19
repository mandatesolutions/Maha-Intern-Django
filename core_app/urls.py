from . import views
from django.urls import path, include

urlpatterns = [
    # path('registration/', views.Registration.as_view(), name='registration'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('notifications/', views.GetAllNotifications.as_view(), name='notifications'),
    path('feedback-questions/', views.FeedbackQuestionListView.as_view(), name='notifications'),
]