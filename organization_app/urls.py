from . import views
from django.urls import path, include

urlpatterns = [

    # Internship operations paths
    path('register-organization',views.RegisterOrganization.as_view(), name='register-organization'),
    path('get-org-profile',views.GetOrgProfile.as_view(), name='get-org-profile'),
    
    path('add-internship', views.Add_Internship.as_view(), name='add-internship'),
    path('get-orginternships/', views.Org_GetInternships.as_view(), name='show-orginternships'), #all internship data to list  on dashboard
    path('get-intern/<str:intern_id>', views.GetInternData.as_view(), name='get-intern'),
    path('update-internship/<str:intern_id>', views.Update_Internship.as_view(), name='update-internship'),
    
    # if required
    path('delete-intern/<str:intern_id>', views.DeleteIntern.as_view(), name='delete-intern'),

    # All Applications for organization

    path('org-all-apps/<str:intern_id>',views.OrganizationAllApps.as_view(), name='register-organization'),
    path('update-apps-status',views.UpdateAppsStatus.as_view(), name='update-apps-status'),

    path('get_student_profile/<int:student_id>',views.GetStudentProfile.as_view(), name='get_student_profile'),

    path('org-dash-counter',views.OrgDashCounter.as_view(), name='org-dash-counter'),

    path('add-monthreport', views.Add_MonthReport.as_view(), name='add-monthreport'),
    path('monthreports/<str:stud_id>', views.MonthReportby_student.as_view(), name='monthreports-bystudent'),

    # CRUD on SelectedStudent table

    path('selected-student-save', views.SelectedStudent.as_view(), name='selected-student-save'),
    path('get-all-selected', views.GetAllSelected.as_view(), name='get-all-selected'),
    path('get-one-selected/<int:selected_id>', views.GetOneSelected.as_view(), name='get-one-selected'),
    path('update-selected-student/<int:selected_id>', views.UpdateSelectedStudent.as_view(), name='update_selected_student'), 
    path('delete-selected-student/<int:selected_id>', views.DeleteSelectedStudent.as_view(), name='delete_selected_student'),
    path('all-selected-applications',views.AllSelectedApps.as_view(),name='all-selected-applications')


]