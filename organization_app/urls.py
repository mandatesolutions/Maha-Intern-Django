from . import views
from django.urls import path, include

urlpatterns = [

    # Internship operations paths
    path('add-intern/', views.AddIntern.as_view(), name='add-intern'),
    # path('update-intern/', views.UpdateIntern.as_view(), name='update-intern'),
    
    
]