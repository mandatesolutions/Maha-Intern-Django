from . import views
from django.urls import path, include

urlpatterns = [
    path('allstudents/', views.Admin_Allstudents.as_view(), name='allstudents'),
]