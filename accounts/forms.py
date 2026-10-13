from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import OwnerProfile, StudentProfile, User
from core.formutils import bootstrapify


class SignUpForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    role = forms.ChoiceField(choices=User.ROLE_CHOICES, widget=forms.RadioSelect)
    email = forms.EmailField(required=True)
    phone = forms.CharField(required=False, max_length=15)

    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'role', 'password1', 'password2']


class StudentProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    class Meta:
        model = StudentProfile
        fields = ['college', 'year_of_study', 'skills', 'availability', 'bio', 'resume']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'skills': forms.TextInput(attrs={'placeholder': 'e.g. tutoring, excel, customer service'}),
            'availability': forms.TextInput(attrs={'placeholder': 'e.g. weekends, evenings'}),
        }


class OwnerProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    class Meta:
        model = OwnerProfile
        fields = ['business_name', 'location', 'contact_info', 'about']
        widgets = {
            'about': forms.Textarea(attrs={'rows': 3, 'placeholder': "A short, friendly line students will see on your job posts."}),
        }


class AIBusinessBlurbForm(forms.Form):
    """A few notes about the business; AI turns them into a short 'about' blurb."""
    notes = forms.CharField(
        label="Tell us about your business in a few words",
        widget=forms.Textarea(attrs={
            'rows': 2,
            'placeholder': "e.g. family-run stationery shop near the college, open evenings, friendly team",
            'data-counter': '200'
        })
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)
