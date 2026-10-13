from django import forms

from .models import Application
from core.formutils import bootstrapify


class ApplicationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        bootstrapify(self)

    class Meta:
        model = Application
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': "Optional note to the owner (why you're a good fit, your availability, etc.)"
            }),
        }
