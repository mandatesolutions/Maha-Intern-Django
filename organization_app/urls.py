from . import views
from django.urls import path, include

urlpatterns = [

    # Internship operations paths
    path('register-organization',views.RegisterOrganization.as_view(), name='register-organization'),
    path('get-org-profile',views.GetOrgProfile.as_view(), name='get-org-profile'),
    
    path('add-intern', views.AddIntern.as_view(), name='add-intern'),
    path('show-internships/<str:organ_id>', views.ShowInternship.as_view(), name='show-internships'), #all internship data to list  on dashboard
    path('get-intern/<str:intern_id>', views.GetInternData.as_view(), name='get-intern'),
    path('update-intern/<str:intern_id>', views.UpdateIntern.as_view(), name='update-intern'),
    
    # if required
    path('delete-intern/<int:intern_id>', views.DeleteIntern.as_view(), name='delete-intern'),

    # All Applications for organization

    path('org-all-apps/<str:intern_id>',views.OrganizationAllApps.as_view(), name='register-organization'),
    path('update-apps-status',views.UpdateAppsStatus.as_view(), name='update-apps-status'),

    path('get_student_profile/<int:student_id>',views.GetStudentProfile.as_view(), name='get_student_profile'),

    path('org-dash-counter',views.OrgDashCounter.as_view(), name='org-dash-counter'),

    path('add-monthreport', views.Add_MonthReport.as_view(), name='add-monthreport'),
    path('monthreports/<str:stud_id>', views.MonthReportby_student.as_view(), name='monthreports-bystudent'),
]