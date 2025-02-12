from django.db import models

# Create your models here.


class District(models.Model):
    district = models.CharField(max_length=155,null=True,blank=True)
    class Meta:
        app_label = 'admin_app'
        db_table = 'District'
        verbose_name = 'District'
        verbose_name_plural = 'Districts'

class Taluka(models.Model):
    district = models.ForeignKey('admin_app.District', on_delete=models.CASCADE, null=True,blank=True)
    taluka =  models.CharField(max_length=155,null=True,blank=True)

    class Meta:
        app_label = 'admin_app'
        db_table = 'Taluka'
        verbose_name = 'Taluka'
        verbose_name_plural = 'Talukas'
