from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
    path('internshipdetails/<str:uid>', views.Student_InternshipDetail.as_view(), name='internshipdetails'),
    path('internship-application/', views.Student_Internshipapply.as_view(), name='internship-application'),
    path('user-applications/', views.Student_Applications.as_view(), name='user-applications'),
]