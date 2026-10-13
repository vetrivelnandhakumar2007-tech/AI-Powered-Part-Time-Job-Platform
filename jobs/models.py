from django.conf import settings
from django.db import models
from django.urls import reverse


class JobCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name_plural = 'Job categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Job(models.Model):
    STATUS_OPEN = 'open'
    STATUS_CLOSED = 'closed'
    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_CLOSED, 'Closed'),
    ]

    PAY_HOURLY = 'hourly'
    PAY_FIXED = 'fixed'
    PAY_TYPE_CHOICES = [
        (PAY_HOURLY, 'Hourly'),
        (PAY_FIXED, 'Fixed'),
    ]

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='jobs')
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.ForeignKey(JobCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='jobs')
    pay_rate = models.DecimalField(max_digits=10, decimal_places=2)
    pay_type = models.CharField(max_length=10, choices=PAY_TYPE_CHOICES, default=PAY_HOURLY)
    location = models.CharField(max_length=200)
    openings = models.PositiveIntegerField(default=1)
    deadline = models.DateField(null=True, blank=True)
    required_skills = models.CharField(max_length=300, blank=True, help_text="Comma-separated, e.g. 'excel, communication'")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # AI-generated / AI-assisted fields
    ai_tags = models.JSONField(blank=True, null=True, help_text="Keywords extracted by AI for matching")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('jobs:job_detail', args=[self.pk])

    def is_open(self):
        return self.status == self.STATUS_OPEN

    def openings_remaining(self):
        filled = self.applications.filter(status='accepted').count()
        return max(self.openings - filled, 0)
