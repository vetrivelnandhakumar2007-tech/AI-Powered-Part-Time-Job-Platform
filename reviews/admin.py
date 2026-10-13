from django.contrib import admin

from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('from_user', 'to_user', 'job', 'rating', 'created_at')
