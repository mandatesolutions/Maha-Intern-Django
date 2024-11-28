from django.db import models
import uuid
# Create your models here.



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

    class Meta:
        db_table = 'Student'
        
    def save(self, *args, **kwargs):
        if not self.stud_id:
            self.stud_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)   