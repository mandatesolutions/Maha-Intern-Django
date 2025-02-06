from . import views
from django.urls import path, include

urlpatterns = [
    path('allstudents/', views.Admin_Allstudents.as_view(), name='allstudents'),
    path('all-organization',views.AllOrganization.as_view(), name='all-organization'),
    path('internships_by_organ/<str:organ_id>',views.InternshipsByOrgan.as_view(), name='internships_by_organ'),
    path('apps-by-intern/<int:intern_id>',views.AppsByIntern.as_view(), name='apps-by-intern'),

    path('get-student-info/<int:student_id>',views.GetStudentInfo.as_view(), name='get-student-info'),
    path('get-organ-info/<int:organ_id>',views.GetOrganInfo.as_view(), name='get-organ-info'),

    # dashboard counter
    path('admin-dashboard-counter', views.AdminDashboardCounter.as_view(), name='admin-dashboard-counter'),
    path('get-student-report/<str:student_id>',views.GetStudentReport.as_view(), name='get-student-report'),

    path('get-joined-students/<str:organ_uid>',views.GetJoinedStudents.as_view(),name='get-joined-students'),
    path('organization-selected-apps/<str:organ_uid>',views.OrgSelectedApps.as_view(),name='organization-selected-apps')








    
]