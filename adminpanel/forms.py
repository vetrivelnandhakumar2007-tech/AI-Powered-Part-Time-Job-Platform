from django import forms

from accounts.models import User
from core.formutils import bootstrapify
from core.models import AboutFeature, HeroSlide, SiteSettings
from jobs.models import Job, JobCategory
from applications.models import Application


class AdminUserForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'role', 'is_active', 'is_staff']
        widgets = {
            'is_active': forms.CheckboxInput(),
            'is_staff': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class AdminJobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'pay_rate', 'pay_type',
            'location', 'openings', 'deadline', 'required_skills', 'status',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class AdminApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'ai_match_score', 'ai_summary']
        widgets = {
            'ai_summary': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class AdminCategoryForm(forms.ModelForm):
    class Meta:
        model = JobCategory
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'tagline', 'footer_about_text', 'support_email', 'support_phone',
            'about_mission_title', 'about_mission_text', 'about_college_heading', 'about_college_text',
        ]
        widgets = {
            'footer_about_text': forms.Textarea(attrs={'rows': 3}),
            'about_mission_text': forms.Textarea(attrs={'rows': 3}),
            'about_college_text': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class HeroSlideForm(forms.ModelForm):
    class Meta:
        model = HeroSlide
        fields = ['eyebrow', 'title', 'subtitle', 'theme', 'image', 'order', 'is_active']
        widgets = {
            'subtitle': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)


class AboutFeatureForm(forms.ModelForm):
    class Meta:
        model = AboutFeature
        fields = ['icon', 'title', 'description', 'order', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)
