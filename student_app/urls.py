from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('dashboard/', views.Student_Dashboard.as_view(), name='dashboard'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
    path('internshipdetails/<str:uid>', views.Student_InternshipDetail.as_view(), name='internshipdetails'),
    path('internship-apply/', views.Student_Internshipapply.as_view(), name='internship-apply'),
    path('user-applications/', views.Student_Applications.as_view(), name='user-applications'),
]