from django.contrib import admin

from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('student', 'job', 'status', 'ai_match_score', 'applied_at')
    list_filter = ('status',)
    search_fields = ('student__username', 'job__title')
