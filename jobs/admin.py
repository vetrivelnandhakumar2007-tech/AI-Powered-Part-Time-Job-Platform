from django.contrib import admin

from .models import Job, JobCategory


@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'category', 'pay_rate', 'pay_type', 'location', 'status', 'created_at')
    list_filter = ('status', 'category', 'pay_type')
    search_fields = ('title', 'description', 'location', 'owner__username')
