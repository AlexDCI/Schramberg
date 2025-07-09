from django import forms
from .models import Participant

class ParticipantLoginForm(forms.Form):
    full_name = forms.CharField(label='full_name')
    email = forms.EmailField(label='Email')

class ParticipantProfileForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ['family_members', 'arrival_date', 'departure_date']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }
