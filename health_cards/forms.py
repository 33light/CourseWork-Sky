from django import forms
from .models import Vote, HealthCard

class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ['status', 'progress']
        widgets = {
            'status': forms.RadioSelect(choices=Vote.STATUS_CHOICES),
            'progress': forms.RadioSelect(choices=Vote.PROGRESS_CHOICES),
        }
