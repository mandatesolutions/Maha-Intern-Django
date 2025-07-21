from . import views
from django.urls import path, include

urlpatterns = [
    path('registration/', views.Student_Registration.as_view(), name='registration'),
    path('dashboard/', views.Student_Dashboard.as_view(), name='dashboard'),
    path('profiledetails/', views.Student_ProfileDetail.as_view(), name='profiledetails'),
    path('education/', views.Student_EducationView.as_view(), name='education'),
    
    path('getinternships/', views.Student_GetInternships.as_view(), name='getinternships'),
    path('search-internships/', views.Search_Internships.as_view(), name='search-internships'),
    path('internshipdetails/<str:uid>', views.Student_InternshipDetail.as_view(), name='internshipdetails'),
    
    path('internship-apply/<str:intern_id>', views.Student_Internshipapply.as_view(), name='internship-apply'),
    path('applications/', views.Student_Applications.as_view(), name='user-applications'),
    
    path('monthreports/', views.ListMonthlyReview.as_view(), name='monthreport'),
    path('monthreports/<str:org_id>', views.CreateMonthlyReview.as_view(), name='add-monthreport'),
    path('monthreport/<str:review_id>', views.MonthlyReviewView.as_view(), name='monthreport'),
    path('received-monthlyreports/', views.RecievedMonthlyReviewView.as_view(), name='received-monthlyreports'),
    
    path('review-organization/<str:org_id>/', views.StudentReviewOrganization.as_view()),
    path('given-reviews/', views.StudentGivenReviews.as_view()),
    path('received-reviews/', views.StudentReceivedReviews.as_view()),
    path('organization-reviews/', views.OrganizationReviewsView.as_view()),
    path('organization-reviews/<str:org_id>/',views.OrganizationReviewsView.as_view()),    
    
    path('give-feedback/<str:org_id>', views.StudentGiveFeedback.as_view(), name='Student-give-feedback'),
    path('feedbacks/given/', views.StudentFeedbacksGiven.as_view(), name='Student-feedbacks-given'),
    path('feedbacks/received/', views.FeedbacksOnStudent.as_view(), name='feedbacks-on-Student'),
    path('feedbacks/organization/', views.FeedbacksForOrganization.as_view(), name='feedbacks-of-all-organization'),
    path('feedbacks/organization/<str:org_id>/', views.FeedbacksForOrganization.as_view(), name='feedbacks-of-specific-organization'),
    
]