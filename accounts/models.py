from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom user with a role: owner or student."""

    ROLE_OWNER = 'owner'
    ROLE_STUDENT = 'student'
    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_STUDENT, 'Student'),
    ]

    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    phone = models.CharField(max_length=15, blank=True)

    def is_owner(self):
        return self.role == self.ROLE_OWNER

    def is_student(self):
        return self.role == self.ROLE_STUDENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class StudentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    college = models.CharField(max_length=200, blank=True)
    year_of_study = models.CharField(max_length=20, blank=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills, e.g. 'tutoring, excel, customer service'")
    availability = models.CharField(max_length=100, blank=True, help_text="e.g. 'weekends, evenings'")
    bio = models.TextField(blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)

    def __str__(self):
        return f"StudentProfile<{self.user.username}>"


class OwnerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='owner_profile')
    business_name = models.CharField(max_length=200)
    location = models.CharField(max_length=200, blank=True)
    contact_info = models.CharField(max_length=200, blank=True)
    about = models.TextField(blank=True)

    def __str__(self):
        return f"OwnerProfile<{self.business_name}>"
