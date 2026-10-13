from django.contrib import admin

from .models import AboutFeature, HeroSlide, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'tagline')

    def has_add_permission(self, request):
        # Singleton — only one row should ever exist.
        return not SiteSettings.objects.exists()


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ('title', 'theme', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('theme', 'is_active')


@admin.register(AboutFeature)
class AboutFeatureAdmin(admin.ModelAdmin):
    list_display = ('title', 'icon', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
