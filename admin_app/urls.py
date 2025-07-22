from . import views
from django.urls import path, include

urlpatterns = [
    path('apps-by-intern/<int:intern_id>',views.AppsByIntern.as_view(), name='apps-by-intern'),

    path('get-student-info/<int:student_id>',views.GetStudentInfo.as_view(), name='get-student-info'),
    path('get-organ-info/<int:organ_id>',views.GetOrganInfo.as_view(), name='get-organ-info'),

    # dashboard counter
    path('admin-dashboard-counter', views.AdminDashboardCounter.as_view(), name='admin-dashboard-counter'),
    path('dashboard-overview/',views.Admin_DashboardOverview.as_view(),name='dashboard-overview'),
    path('latest-registered-student',views.LatestStudent.as_view(),name='latest-registered-student'),
    path('get-student-report/<str:student_id>',views.GetStudentReport.as_view(), name='get-student-report'),

    path('get-joined-students/<str:organ_uid>',views.GetJoinedStudents.as_view(),name='get-joined-students'),
    path('organization-selected-apps/<str:organ_uid>',views.OrgSelectedApps.as_view(),name='organization-selected-apps'),

    path('feedback-questions/<str:feedback_for>', views.Admin_FeedbackQuestionsView.as_view(), name='feedback-questions'),  
    
    # Internships APIs    
    path('internships/',views.Admin_InternshipListCreateView.as_view(), name='get-create-internship'),
    path('internship/<str:intern_id>/status/<str:intern_status>/',views.Admin_ApproveBlockInternship.as_view(), name='approve-block-internship'),
    
    # Organization APIs
    path('organizations/',views.Admin_OrganizationListCreateView.as_view(), name='all-create-organization'),
    path('organization/<str:org_id>',views.Admin_RetrieveUpdateDestroyOrganizationView.as_view(), name='get-update-delete-organization'),
    path('organization/<str:org_id>/status/<str:org_status>/', views.Admin_ApproveBlockOrganizationView.as_view(), name='approve-block-organization'),
    
    # Student APIs
    path('students/', views.Admin_StudentsListView.as_view(), name='allstudents'),
    path('student/<str:stud_id>', views.Admin_RetrieveStudentView.as_view(), name='get-student'),
    path('student/<str:stud_id>/status/<str:stud_status>/', views.Admin_BlockUnBlockStudentView.as_view(), name='approve-block-student'),
]