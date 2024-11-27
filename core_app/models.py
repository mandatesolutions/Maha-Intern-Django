from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # Encrypt the password using set_password
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(email, password, **extra_fields)


class UserModel(AbstractUser):
    ROLE_CHOICES = (
        ("Admin", "Admin"),
        ("Student", "Student"),
        ("Organization", "Organization"),
    )

    
    email = models.EmailField(unique=True)  # Ensure the email is unique
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, blank=True, null=True)
    mobile = models.CharField(max_length=15, blank=True, null=True)
    

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name'] 

    objects = CustomUserManager()

    class Meta:
        db_table = 'UserModel'

    def __str__(self):
        return self.email



