from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
import uuid

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
    username = None

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] 

    objects = CustomUserManager()

    class Meta:
        db_table = 'UserModel'

    def __str__(self):
        return self.email

class Notification(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    user = models.ForeignKey(UserModel, on_delete=models.CASCADE)
    redirect_url = models.CharField(max_length=255, null=True, blank=True)

    class Meta:
        db_table = 'Notification'
        
class Review(models.Model):
    REVIEW_FROM_CHOICES = [
        ('student', 'Student'),
        ('organization', 'Organization'),
    ]

    review_id = models.CharField(max_length=100, unique=True, editable=False, null=True, blank=True)
    reviewer_type = models.CharField(max_length=20, choices=REVIEW_FROM_CHOICES)
    
    reviewer_student = models.ForeignKey(
        'student_app.student',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='student_given_reviews'
    )

    reviewer_organization = models.ForeignKey(
        'organization_app.organization',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='organization_given_reviews'
    )

    reviewed_student = models.ForeignKey(
        'student_app.student',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='student_received_reviews'
    )

    reviewed_organization = models.ForeignKey(
        'organization_app.organization',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='organization_received_reviews'
    )

    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.reviewer_type} review"

    def save(self, *args, **kwargs):
        if not self.review_id:
            self.review_id = str(uuid.uuid4())
        super().save(*args, **kwargs)
        
    class Meta:
        db_table = 'Review'
        ordering = ['-created_at']
        
        
class FeedbackQuestion(models.Model):
    FEEDBACK_FOR_CHOICES = (
        ('student', 'For Student'),
        ('organization', 'For Organization'),
    )

    question_id = models.AutoField(primary_key=True)
    question_text = models.CharField(max_length=255)
    feedback_for = models.CharField(max_length=20, choices=FEEDBACK_FOR_CHOICES)

    def __str__(self):
        return f"[{self.feedback_for}] {self.question_text}"

    class Meta:
        db_table = 'FeedbackQuestion'


class FeedbackResponse(models.Model):
    FEEDBACK_TYPE_CHOICES = (
        ('student_to_organisation', 'Student to Organisation'),
        ('organisation_to_student', 'Organisation to Student'),
    )

    feedback_id = models.CharField(max_length=100, unique=True, editable=False, null=True, blank=True)

    # New sender-recipient mapping
    sender_student = models.ForeignKey(
        'student_app.student',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='feedbacks_sent_by_student'
    )
    sender_organization = models.ForeignKey(
        'organization_app.organization',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='feedbacks_sent_by_organization'
    )

    recipient_student = models.ForeignKey(
        'student_app.student',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='feedbacks_received_by_student'
    )
    recipient_organization = models.ForeignKey(
        'organization_app.organization',
        null=True, blank=True,
        on_delete=models.CASCADE,
        related_name='feedbacks_received_by_organization'
    )

    feedback_type = models.CharField(max_length=30, choices=FEEDBACK_TYPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback {self.feedback_id}"

    def save(self, *args, **kwargs):
        if not self.feedback_id:
            self.feedback_id = str(uuid.uuid4()).replace('-', '')
        super().save(*args, **kwargs)

    class Meta:
        db_table = 'FeedbackResponse'
        ordering = ['-created_at']


class FeedbackAnswer(models.Model):
    response = models.ForeignKey(FeedbackResponse, related_name='answers', on_delete=models.CASCADE)
    question = models.ForeignKey(FeedbackQuestion, on_delete=models.CASCADE)
    answer_text = models.TextField()

    def __str__(self):
        return f"Answer to: {self.question.question_text}"

    class Meta:
        db_table = 'FeedbackAnswer'
