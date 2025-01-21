from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('getinternships/', views.Student_GetInternships.as_view(), name='getinternships'),
    path('search-internships/', views.Search_Internships.as_view(), name='search-internships'),
    path('dashboard/', views.Student_Dashboard.as_view(), name='dashboard'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
    path('internshipdetails/<str:uid>', views.Student_InternshipDetail.as_view(), name='internshipdetails'),
    path('internship-apply/', views.Student_Internshipapply.as_view(), name='internship-apply'),
    path('stud-applications/', views.Student_Applications.as_view(), name='user-applications'),
    path('stud-applications-status/<str:stat>/', views.Applicationsby_status.as_view(), name='applicationsby-status'),
]