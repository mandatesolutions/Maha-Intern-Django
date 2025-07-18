from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('dashboard/', views.Student_Dashboard.as_view(), name='dashboard'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
    
    path('getinternships/', views.Student_GetInternships.as_view(), name='getinternships'),
    path('search-internships/', views.Search_Internships.as_view(), name='search-internships'),
    path('internshipdetails/<str:uid>', views.Student_InternshipDetail.as_view(), name='internshipdetails'),
    
    path('internship-apply/<str:intern_id>', views.Student_Internshipapply.as_view(), name='internship-apply'),
    path('applications/', views.Student_Applications.as_view(), name='user-applications'),
    
    path('education/', views.Student_EducationView.as_view(), name='education'),
]