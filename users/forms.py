from django import forms
from .models import Participant, Registration,Adult, Child
from django.forms import inlineformset_factory
from django.contrib.auth.hashers import make_password
from django.core.exceptions import ValidationError
import re

class ParticipantRegisterForm(forms.ModelForm):
    privacy_accepted = forms.BooleanField(
        label="Ich habe die Datenschutzerklärung gelesen und akzeptiere sie",
        required=True
    )

    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Passwort",
        min_length=8,
        help_text="Mindestens 8 Zeichen, inkl. Buchstaben und Zahlen."
    )

    class Meta:
        model = Participant
        fields = ['first_name', 'last_name', 'email', 'password', 'privacy_accepted']

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if not any(c.isdigit() for c in pwd) or not any(c.isalpha() for c in pwd):
            raise ValidationError("Das Passwort muss Buchstaben und Zahlen enthalten.")
        return pwd

    def clean_privacy_accepted(self):
        if not self.cleaned_data.get('privacy_accepted'):
            raise ValidationError("Bitte akzeptieren Sie die Datenschutzerklärung.")
        return True

    def save(self, commit=True):
        participant = super().save(commit=False)
        participant.password = make_password(self.cleaned_data['password'])  # хэшируем пароль!
        if commit:
            participant.save()
        return participant

class ParticipantSetNewPasswordForm(forms.Form):
    new_password1 = forms.CharField(widget=forms.PasswordInput, label="Новый пароль")
    new_password2 = forms.CharField(widget=forms.PasswordInput, label="Подтверждение пароля")

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get("new_password1")
        p2 = cleaned_data.get("new_password2")
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError("Пароли не совпадают.")
        return cleaned_data



class ParticipantPasswordResetRequestForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=254)

    def clean_email(self):
        email = self.cleaned_data['email']
        if not Participant.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email не найден.")
        return email


class ParticipantLoginForm(forms.Form):
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput,
    )

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if len(pwd) < 8 or not any(c.isdigit() for c in pwd) or not any(c.isalpha() for c in pwd):
            raise forms.ValidationError('Das Passwort muss mindestens 8 Zeichen lang sein und Buchstaben sowie Zahlen enthalten.')
        return pwd
    

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = [
            'leisure_activities',
            'church_contact',
            'needs_transport',
            'has_dietary_restrictions',
            'dietary_details',
            'comment',
        ]
        widgets = {
            'leisure_activities': forms.Textarea(attrs={'rows': 2}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        
class AdultForm(forms.ModelForm):
    SERVICES_CHOICES = [
        ('guitar', 'Gitarre'),
        ('piano', 'Klavier'),
        ('kids_small', 'Kleinkinder'),
        ('kids_kiga', 'Kiga'),
        ('kids_school', 'Schüler'),
        ('chairs', 'Stuhldienst'),
        ('tech', 'Technik'),
        ('microphones', 'Mikrofondienst'),
    ]
    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dienste"
    )

    class Meta:
        model = Adult
        exclude = ['registration']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.services:
            self.fields['services'].initial = self.instance.services.split(',')

    def clean_services(self):
        return ','.join(self.cleaned_data['services'])

class ChildForm(forms.ModelForm):
    SERVICES_CHOICES = [
        ('guitar', 'Gitarre'),
        ('piano', 'Klavier'),
        ('kids_small', 'Kleinkinder'),
        ('kids_kiga', 'Kiga'),
        ('kids_school', 'Schüler'),
        ('chairs', 'Stuhldienst'),
        ('tech', 'Technik'),
        ('microphones', 'Mikrofondienst'),
    ]
    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Dienste"
    )

    class Meta:
        model = Child
        exclude = ['registration']
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.services:
            self.fields['services'].initial = self.instance.services.split(',')

    def clean_services(self):
        return ','.join(self.cleaned_data['services'])

def clean(self):
    cleaned_data = super().clean()
    # if cleaned_data.get('has_children') and not cleaned_data.get('children_ages'):
    #     self.add_error('children_ages', 'Bitte geben Sie das Alter der Kinder an.')
    if cleaned_data.get('has_dietary_restrictions') and not cleaned_data.get('dietary_details'):
        self.add_error('dietary_details', 'Bitte geben Sie Details zu den Ernährungseinschränkungen an.')
    if not cleaned_data.get('privacy_accepted'):
        self.add_error('privacy_accepted', 'Bitte akzeptieren Sie die Datenschutzerklärung.')