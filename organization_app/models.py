from django.db import models
from core_app.models import UserModel
from datetime import date
import uuid

current_year = date.today().year

# # Create your models here.

class Organization(models.Model):
    industry_type_choices= (
        ("Public Sectors","Public Sectors"),
        ("Private Sectors","Private Sectors"),
        ("Government Organizations","Government Organizations"),
        ("Non-Governmental Organizations","Non-Governmental Organizations"),
        ("Corporate Sectors","Corporate Sectors")
    )
    
    org_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    user = models.OneToOneField('core_app.Usermodel', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=512,blank=True,null=True)
    industry_type = models.CharField(max_length=255,null=True,blank=True,choices=industry_type_choices)
    company_id_type = models.CharField(max_length=50,null=True,blank=True)
    company_unique_id = models.CharField(max_length=100,null=True,blank=True)
    reprsentative_name = models.CharField(max_length=255,null=True,blank=True)
    district = models.CharField(max_length=155,null=True,blank=True)
    taluka = models.CharField(max_length=155,null=True,blank=True)
    organization_logo = models.FileField(upload_to='company_logo/',null=True,blank=True)
    profile = models.FileField(upload_to='company_profile/',null=True,blank=True)
    is_approved = models.BooleanField(default=False)
    

    class Meta:
        app_label = 'organization_app'
        db_table = 'Organization'
        ordering = ['-id']

    def __str__(self):
        return self.company_name
    
    def save(self, *args, **kwargs):
        if not self.org_id:
            self.org_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
    

# Internship model
class Internship(models.Model):
    intern_type_choices= (
        ("Part Time","Part Time"),
        ("Full Time","Full Time"),
        ("Virtual","Virtual"),
    )
    
    stipend_type_choices= (
        ("Paid","Paid"),
        ("Unpaid","Unpaid"),
    )

    intern_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    intern_type = models.CharField(max_length=55,null=True,blank=True,choices=intern_type_choices)
    company = models.ForeignKey('organization_app.Organization', on_delete=models.CASCADE, related_name='company_internships',null=True,blank=True)  # Company is a User
    title = models.CharField(max_length=100,null=True)
    description = models.TextField(null=True,blank=True)
    no_of_openings = models.IntegerField(null=True,blank=True)
    stipend_type = models.CharField(max_length=55,null=True,blank=True,choices=stipend_type_choices)
    stipend_amount = models.FloatField(blank=True,null=True,default=0)
    location = models.CharField(max_length=100,blank=True,null=True)
    duration = models.IntegerField(null=True,blank=True)  # duration in month
    skills_required = models.TextField(null=True,blank=True)
    contact_email = models.EmailField(null=True,blank=True)  
    contact_mobile = models.CharField(max_length=15, blank=True, null=True)
    start_date = models.DateField(null=True,blank=True)
    last_date_of_apply = models.DateField(null=True,blank=True)
    perks = models.TextField(null=True,blank=True)
    qualification_in = models.CharField(max_length=1000,blank=True,null=True)
    specialisation_in = models.CharField(max_length=1000,blank=True, null=True)
    terms = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)

    class Meta:
        app_label = 'organization_app'
        db_table = 'Internship'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.intern_id:
            self.intern_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
    
# Application model (students applying for internships)

APPLICATION_STATUS_CHOICES = [
        ('pending', 'pending'),
        ('shortlisted', 'shortlisted'),
        ('selected', 'selected'),
        ('rejected', 'rejected'),
        ('accepted', 'accepted'),
        ('declined', 'declined'),
    ]
class Application(models.Model):
    
    app_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    student = models.ForeignKey('student_app.Student', on_delete=models.CASCADE, related_name='student_applications', blank=True, null=True)  # Student is a User
    internship = models.ForeignKey('organization_app.Internship', on_delete=models.CASCADE,null=True,blank=True, related_name="internship_applications")
    applied_on = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES, default='pending')
    updated_at = models.DateTimeField(auto_now=True,null=True,blank=True)
    def __str__(self):
        return f"{self.app_id}"
    
    class Meta:
        app_label = 'organization_app'
        db_table = 'Application'
        ordering = ['-applied_on']
    
    def save(self, *args, **kwargs):
        if not self.app_id:
            self.app_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)

class InterviewDetails(models.Model):
    interview_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    application = models.OneToOneField('Application', on_delete=models.CASCADE, related_name='application_interview')
    date = models.DateField()
    time = models.TimeField()
    mode = models.CharField(max_length=100)  # Online / Offline
    location = models.TextField(blank=True, null=True)
    instructions = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'interview_details'
    
    def __str__(self):
        return f"Interview for {self.application}"
    
    def save(self, *args, **kwargs):
        if not self.interview_id:
            self.interview_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)

class OfferDetails(models.Model):
    offer_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    application = models.OneToOneField('Application', on_delete=models.CASCADE, related_name='application_offer')
    joining_date = models.DateField()
    offer_letter_file = models.FileField(upload_to='candidate/offers/')
    other_details = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'offer_details'
        
    def __str__(self):
        return f"Offer for {self.application}"
    
    def save(self, *args, **kwargs):
        if not self.offer_id:
            self.offer_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)

class ApplicationStatusHistory(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='status_history')
    old_status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES)
    new_status = models.CharField(max_length=20, choices=APPLICATION_STATUS_CHOICES)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'application_status_history'
        
    def __str__(self):
        return f'{self.application.app_id}: {self.old_status} → {self.new_status}'


class SelectedStudentModel(models.Model):
    selected_student_id = models.CharField(max_length=100, unique=True, editable=False, null=True)    
    application = models.OneToOneField('organization_app.Application', on_delete=models.CASCADE, related_name='selected_student')
    joining_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=20, choices=[('Joined', 'Joined'), ('Completed', 'Completed')], default='Joined')

    class Meta:
        app_label = 'organization_app'
        db_table = 'SelectedStudentModel'
        
    def __str__(self):
        return f"{self.selected_student_id}"
    
    def save(self, *args, **kwargs):
        if not self.selected_student_id:
            self.selected_student_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)



class MonthlyReviewOrganizationToStudent(models.Model):
    
    MONTHS = [
        ('January', 'January'),
        ('February', 'February'),
        ('March', 'March'),
        ('April', 'April'),
        ('May', 'May'),
        ('June', 'June'),
        ('July', 'July'),
        ('August', 'August'),
        ('September', 'September'),
        ('October', 'October'),
        ('November', 'November'),
        ('December', 'December'),
    ]
    
    review_id = models.CharField(max_length=50, unique=True, editable=False, null=True)
    organization = models.ForeignKey(
        'organization_app.Organization',
        on_delete=models.CASCADE,
        related_name='monthly_reviews_given_to_students'
    )
    student = models.ForeignKey(
        'student_app.Student',
        on_delete=models.CASCADE,
        related_name='monthly_reviews_received_from_organization'
    )
    month = models.CharField(max_length=50, choices=MONTHS)
    year = models.IntegerField(auto_created=True, default=current_year)
    review_content = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'monthly_reviews_organization_to_student'
        unique_together = ('student', 'organization', 'month', 'year')
        
    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
