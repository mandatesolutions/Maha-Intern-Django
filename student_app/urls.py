from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
]