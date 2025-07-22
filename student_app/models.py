from django.db import models
import uuid
from django.core.validators import MaxValueValidator, MinValueValidator
from datetime import date

current_year = date.today().year



class Student(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
    
    stud_id = models.CharField(max_length=100, unique=True, editable=False, null=True)
    user = models.OneToOneField('core_app.Usermodel', on_delete=models.CASCADE)
    adhar_number = models.CharField(null=True,blank=True,max_length=12)
    district = models.CharField(max_length=155, null=True, blank=True)
    taluka = models.CharField(max_length=155, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    last_course =  models.CharField(max_length=255, null=True, blank=True)
    university =  models.CharField(max_length=255, null=True, blank=True)
    profile = models.TextField(max_length=500, blank=True, null=True)
    language = models.CharField(max_length=500, blank=True, null=True)
    skills = models.TextField(max_length=1500, blank=True, null=True)
    is_blocked = models.BooleanField(default=False)
    
    resume = models.FileField(upload_to='Candidate/resume/', null=True, blank=True)
    cover_letter = models.FileField(upload_to='Candidate/cover_letter/', null=True, blank=True)
    profile_pic = models.ImageField(upload_to='Candidate/profile_pic/', null=True, blank=True)
    
    is_education_filled = models.BooleanField(default=False)

    class Meta:
        db_table = 'Student'
        ordering = ['-id']
        
    def save(self, *args, **kwargs):
        if not self.stud_id:
            self.stud_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)   
        
class Education(models.Model):    
    student = models.OneToOneField('Student', on_delete=models.CASCADE, related_name="student_education")
    
    ssc_passing_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)])
    ssc_board = models.CharField(max_length=255)
    ssc_percentage = models.IntegerField(validators=[MinValueValidator(35), MaxValueValidator(100)])
    
    hsc_passing_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)],null=True,blank=True)
    hsc_board = models.CharField(max_length=255,null=True,blank=True)
    hsc_college = models.CharField(max_length=255,null=True,blank=True)
    hsc_stream = models.CharField(max_length=255,null=True,blank=True)
    hsc_percentage = models.IntegerField(validators=[MinValueValidator(35), MaxValueValidator(100)],null=True,blank=True)
    
    grad_course = models.CharField(max_length=255, blank=True, null=True)
    grad_stream = models.CharField(max_length=255, blank=True, null=True)
    grad_from_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)],null=True,blank=True)
    grad_to_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)],null=True,blank=True)
    grad_university = models.CharField(max_length=255, blank=True, null=True)
    grad_college = models.CharField(max_length=255, blank=True, null=True)
    grad_percentage = models.IntegerField(validators=[MinValueValidator(35), MaxValueValidator(100)],null=True,blank=True)
    
    pg_course = models.CharField(max_length=255, blank=True, null=True)
    pg_stream = models.CharField(max_length=255, blank=True, null=True)
    pg_from_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)],null=True,blank=True)
    pg_to_year = models.IntegerField(validators=[MinValueValidator(1900), MaxValueValidator(current_year)],null=True,blank=True)
    pg_university = models.CharField(max_length=255, blank=True, null=True)
    pg_college = models.CharField(max_length=255, blank=True, null=True)
    pg_percentage = models.IntegerField(validators=[MinValueValidator(35), MaxValueValidator(100)],null=True,blank=True)
    
    
    class Meta:
        db_table = 'education'
    
class MonthlyReviewStudentToOrganization(models.Model):
    
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
        related_name='monthly_reviews_received_from_students'
    )
    student = models.ForeignKey(
        'student_app.Student',
        on_delete=models.CASCADE,
        related_name='monthly_reviews_given_to_organizations'
    )

    month = models.CharField(max_length=50, choices=MONTHS)
    year = models.IntegerField(auto_created=True, default=current_year)
    review_content = models.TextField(null=True, blank=True)
    feedback = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'monthly_reviews_student_to_organization'
        unique_together = ('student', 'organization', 'month', 'year')
        
    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)
