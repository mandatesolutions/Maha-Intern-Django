from . import views
from django.urls import path, include

urlpatterns = [

    # Internship operations paths
    path('district_list', views.DistrictList.as_view(), name='district_list'),
    path('taluka_list/<int:district_id>', views.TalukaList.as_view(), name='taluka_list'),
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
    path('application/<str:app_id>/status/<str:app_status>',views.UpdateAppsStatus.as_view(), name='update-apps-status'),
    path('application/<str:app_id>/interview/', views.Org_InterviewDetailsView.as_view(), name='application-interview'),
    path('application/<str:app_id>/offer/', views.Org_OfferDetailsView.as_view(), name='application-interview'),

    path('get_student_profile/<int:student_id>',views.GetStudentProfile.as_view(), name='get_student_profile'),

    path('org-dash-counter',views.OrgDashCounter.as_view(), name='org-dash-counter'),

    path('monthreports/', views.ListMonthlyReview.as_view(), name='monthreport'),
    path('monthreports/<str:stud_id>', views.CreateMonthlyReview.as_view(), name='add-monthreport'),
    path('monthreport/<str:review_id>', views.MonthlyReviewView.as_view(), name='monthreport'),
    path('received-monthlyreports/', views.RecievedMonthlyReviewView.as_view(), name='received-monthlyreports'),
    

    # CRUD on SelectedStudent table

    path('selected-student-save', views.SelectedStudent.as_view(), name='selected-student-save'),
    path('get-all-selected', views.GetAllSelected.as_view(), name='get-all-selected'),
    path('get-one-selected/<str:selected_id>', views.GetOneSelected.as_view(), name='get-one-selected'),
    path('update-selected-student/<str:selected_id>', views.UpdateSelectedStudent.as_view(), name='update_selected_student'), 
    path('delete-selected-student/<str:selected_id>', views.DeleteSelectedStudent.as_view(), name='delete_selected_student'),
    path('all-selected-applications',views.AllSelectedApps.as_view(),name='all-selected-applications'),
    
    path('review-student/<str:stud_id>/', views.OrganizationReviewStudent.as_view()),
    path('given-reviews/', views.OrganizationGivenReviews.as_view()),
    path('received-reviews/', views.OrganizationReceivedReviews.as_view()),
    path('student-reviews/', views.OrganizationViewStudentReviews.as_view()),
    path('student-reviews/<str:stud_id>/', views.OrganizationViewStudentReviews.as_view()),
    
    
    path('give-feedback/<str:stud_id>', views.OrganizationGiveFeedbackToStudent.as_view(), name='company-give-feedback'),
    path('feedbacks/given/', views.OrganizationFeedbacksGiven.as_view(), name='company-feedbacks-given'),
    path('feedbacks/received/', views.FeedbacksGivenOnOrganization.as_view(), name='feedbacks-on-company'),
    path('feedbacks/students/', views.FeedbacksOfStudentForOrganization.as_view(), name='feedbacks-of-all-students'),
    path('feedbacks/students/<str:stud_id>/', views.FeedbacksOfStudentForOrganization.as_view(), name='feedbacks-of-specific-student'),


]