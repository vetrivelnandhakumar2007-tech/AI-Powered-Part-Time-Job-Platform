from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import OwnerProfile, StudentProfile, User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Namma Ooru Jobs', {'fields': ('role', 'phone')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Namma Ooru Jobs', {'fields': ('role', 'phone', 'email')}),
    )


@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'college', 'year_of_study', 'availability')
    search_fields = ('user__username', 'college', 'skills')


@admin.register(OwnerProfile)
class OwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'location')
    search_fields = ('business_name', 'location')
