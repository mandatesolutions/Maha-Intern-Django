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
    
 