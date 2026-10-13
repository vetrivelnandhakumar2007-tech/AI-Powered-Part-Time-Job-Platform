from django.conf import settings
from django.db import models


class Application(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_ACCEPTED = 'accepted'
    STATUS_REJECTED = 'rejected'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    job = models.ForeignKey('jobs.Job', on_delete=models.CASCADE, related_name='applications')
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='applications')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    # AI-generated fields
    ai_match_score = models.FloatField(null=True, blank=True, help_text="0-100 relevance score")
    ai_summary = models.TextField(blank=True, help_text="AI one-line summary of the applicant for the owner")

    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'student')
        ordering = ['-ai_match_score', '-applied_at']

    def __str__(self):
        return f"{self.student} -> {self.job} ({self.status})"
