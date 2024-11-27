from . import views
from django.urls import path, include

urlpatterns = [

    # Internship operations paths
    path('register-organization',views.RegisterOrganization.as_view(), name='register-organization'),
    path('get-org-profile',views.GetOrgProfile.as_view(), name='get-org-profile'),
    
    path('add-intern', views.AddIntern.as_view(), name='add-intern'),
    path('show-internships', views.ShowInternship.as_view(), name='show-internships'), #all internship data to list  on dashboard
    path('get-intern/<int:intern_id>', views.GetInternData.as_view(), name='get-intern'),
    path('update-intern/<int:intern_id>', views.UpdateIntern.as_view(), name='update-intern'),
    
    
]