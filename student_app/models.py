from django.db import models

# Create your models here.



class Student(models.Model):
    GENDER_CHOICES = (
        ("Male", "Male"),
        ("Female", "Female"),
    )
   
    user = models.OneToOneField('core_app.Usermodel', on_delete=models.CASCADE)
    adhar_number = models.IntegerField(null=True,blank=True)
    district = models.CharField(max_length=155, null=True, blank=True)
    taluka = models.CharField(max_length=155, null=True, blank=True)
    dob = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, blank=True, null=True)
    last_course =  models.CharField(max_length=255, null=True, blank=True)
    university =  models.CharField(max_length=255, null=True, blank=True)


    