from django import forms

from .models import Job, JobCategory
from core.formutils import bootstrapify


class JobForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    class Meta:
        model = Job
        fields = [
            'title', 'description', 'category', 'pay_rate', 'pay_type',
            'location', 'openings', 'deadline', 'required_skills',
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 5}),
            'deadline': forms.DateInput(attrs={'type': 'date'}),
            'required_skills': forms.TextInput(attrs={'placeholder': 'e.g. excel, communication, punctuality'}),
        }


class AIJobDraftForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    """Owner types a rough idea; AI turns it into a structured draft."""
    raw_idea = forms.CharField(
        label="Describe the job in a few words",
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': "e.g. need someone for weekend shop help, evenings, near college",
            'data-counter': '300'
        })
    )


class JobSearchForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    q = forms.CharField(required=False, label='', widget=forms.TextInput(
        attrs={'placeholder': 'Search jobs, e.g. "evening tutoring near campus"'}))
    category = forms.ModelChoiceField(required=False, queryset=JobCategory.objects.all(), label='Category')
    location = forms.CharField(required=False, label='Location')
