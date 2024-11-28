from . import views
from django.urls import path, include

urlpatterns = [
    path('allstudents/', views.Admin_Allstudents.as_view(), name='allstudents'),
    path('all-organization',views.AllOrganization.as_view(), name='all-organization'),
    path('internships_by_organ/<int:organ_id>',views.InternshipsByOrgan.as_view(), name='internships_by_organ')
    
]