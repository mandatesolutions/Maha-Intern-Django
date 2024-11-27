from django.db import models
from core_app.models import UserModel
import uuid

# # Create your models here.

class Organization(models.Model):
    industry_type_choices= (
        ("Public Sectors","Public Sectors"),
        ("Private Sectors","Private Sectors"),
        ("Government Organizations","Government Organizations"),
        ("Non-Governmental Organizations","Non-Governmental Organizations"),
        ("Corporate Sectors","Corporate Sectors")
    )
    user = models.OneToOneField('core_app.Usermodel', on_delete=models.CASCADE)
    company_name = models.CharField(max_length=512,blank=True,null=True)
    industry_type = models.CharField(max_length=255,null=True,blank=True,choices=industry_type_choices)
    company_id_type = models.CharField(max_length=50,null=True,blank=True)
    company_unique_id = models.CharField(max_length=100,null=True,blank=True)
    reprsentative_name = models.CharField(max_length=255,null=True,blank=True)
    district = models.CharField(max_length=155,null=True,blank=True)
    taluka = models.CharField(max_length=155,null=True,blank=True)
    organization_logo = models.FileField(upload_to='company_logo/',null=True,blank=True)
    

    class Meta:
        app_label = 'organization_app'
        db_table = 'Organization'

    def __str__(self):
        return self.company_name
    

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
    location = models.CharField(max_length=100,blank=True,null=True)
    duration = models.IntegerField(null=True,blank=True)  # duration in month
    skills_required = models.TextField(null=True,blank=True)
    contact_email = models.EmailField(null=True, blank=True)
    contact_mobile = models.CharField(max_length=15, blank=True, null=True)
    start_date = models.DateField(null=True,blank=True)
    last_date_of_apply = models.DateField(null=True,blank=True)
    perks = models.TextField(null=True,blank=True)
    qualification_in = models.CharField(max_length=1000,blank=True,null=True)
    specialisation_in = models.CharField(max_length=1000,blank=True, null=True)
    terms = models.TextField(null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = 'organization_app'
        db_table = 'Internship'
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.intern_id:
            self.intern_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
    
# Application model (students applying for internships)
class Application(models.Model):
    student = models.ForeignKey('core_app.Usermodel', on_delete=models.CASCADE, related_name='applications')  # Student is a User
    internship = models.ForeignKey('organization_app.Internship', on_delete=models.CASCADE,null=True,blank=True)
    applied_on = models.DateTimeField(auto_now_add=True)
    resume = models.FileField(upload_to='apps_resumes/',null=True,blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected')], default='pending')
    
    def __str__(self):
        return f"{self.student.username} applied for {self.internship.title}"
    
    class Meta:
        app_label = 'organization_app'
        db_table = 'Application'
    

