from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Registration.as_view(), name='registration'),
    #login api for user 
    path('login/', views.LoginView.as_view(), name='login'),
]