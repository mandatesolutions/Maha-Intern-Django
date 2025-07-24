from . import views
from django.urls import path, include

urlpatterns = [

    # dashboard counter
    path('admin-dashboard-counter', views.AdminDashboardCounter.as_view(), name='admin-dashboard-counter'),
    path('dashboard-overview/',views.Admin_DashboardOverview.as_view(),name='dashboard-overview'),
    path('latest-registered-student',views.LatestStudent.as_view(),name='latest-registered-student'),

    path('get-joined-students/<str:organ_uid>',views.GetJoinedStudents.as_view(),name='get-joined-students'),
    path('organization-selected-apps/<str:organ_uid>',views.OrgSelectedApps.as_view(),name='organization-selected-apps'),

    
    # Reports, Reviews, Feedbacks APIs
    path('mothly-report/students/',views.Admin_ListMonthlyReportofStudent.as_view(), name='get-student-report'),
    path('mothly-report/organization/',views.Admin_ListMonthlyReportofOrganization.as_view(), name='get-organization-report'),
    path('reviews/',views.Admin_ReviewsListView.as_view(), name='all-reviews'),
    path('feedback-questions/<str:feedback_for>', views.Admin_FeedbackQuestionsView.as_view(), name='feedback-questions'),  
    path('feedbacks/students/', views.Admin_FeedbacksOfStudent.as_view(), name='feedbacks-of-all-students'),
    path('feedbacks/organization/', views.Admin_FeedbacksOfOrganization.as_view(), name='feedbacks-of-all-organization'),
    
    # Internships APIs    
    path('internships/',views.Admin_InternshipListView.as_view(), name='get-create-internship'),
    path('internships/<str:org_id>',views.Admin_InternshipCreateView.as_view(), name='create-internship'),
    path('internship/<str:intern_id>',views.Admin_InternshipRetrieveUpdateDeleteView.as_view(), name='get-update-delete-internship'),
    path('internship/<str:intern_id>/status/<str:intern_status>/',views.Admin_ApproveBlockInternship.as_view(), name='approve-block-internship'),
    
    # Internship Applications APIs
    path('apps-by-intern/<int:intern_id>',views.AppsByIntern.as_view(), name='apps-by-intern'),
    path('applications/',views.Admin_ApplicationsListView.as_view(), name='all-applications'), 
    path('applications/<str:app_id>',views.Admin_RetrieveApplication.as_view(), name='all-applications'),
    path('application/<str:app_id>/interview/', views.Admin_InterviewDetailsView.as_view(), name='application-interview'), 
    
    # Organization APIs
    path('organizations/',views.Admin_OrganizationListCreateView.as_view(), name='all-create-organization'),
    path('organization/<str:org_id>',views.Admin_RetrieveUpdateDestroyOrganizationView.as_view(), name='get-update-delete-organization'),
    path('organization/<str:org_id>/status/<str:org_status>/', views.Admin_ApproveBlockOrganizationView.as_view(), name='approve-block-organization'),
    
    # Student APIs
    path('students/', views.Admin_StudentsListView.as_view(), name='allstudents'),
    path('student/<str:stud_id>', views.Admin_RetrieveStudentView.as_view(), name='get-student'),
    path('student/<str:stud_id>/status/<str:stud_status>/', views.Admin_BlockUnBlockStudentView.as_view(), name='approve-block-student'),
    path('student-resumes/', views.Admin_StudentResumesListView.as_view(), name='student-resumes'),
    path('forward-student-profile/', views.Admin_ForwardStudentProfileToOrganization.as_view(), name='forward-student-profile'),
    path('download-student-resume/<str:stud_id>', views.Admin_DownloadStudentResume.as_view(), name='download-student-resume'),
]