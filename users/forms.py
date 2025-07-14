from django import forms
from .models import Participant, Child
from django.forms import inlineformset_factory
import re

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
        if not Participant.objects.filter(email=email).exists():
            raise forms.ValidationError("Email не найден.")
        return email


class ParticipantLoginForm(forms.Form):
    first_name = forms.CharField(label='Vorname')
    last_name = forms.CharField(label='Nachname')
    email = forms.EmailField(label='Email')
    password = forms.CharField(
        label='Passwort',
        widget=forms.PasswordInput,
        help_text='Mindestens 8 Zeichen, Buchstaben und Zahlen'
    )

    def clean_password(self):
        pwd = self.cleaned_data['password']
        if len(pwd) < 8 or not any(c.isdigit() for c in pwd) or not any(c.isalpha() for c in pwd):
            raise forms.ValidationError('Das Passwort muss mindestens 8 Zeichen lang sein und Buchstaben sowie Zahlen enthalten.')
        return pwd


class ChildForm(forms.ModelForm):
    class Meta:
        model = Child
        fields = ['name', 'age']
        labels = {
            'name': 'Name des Kindes',
            'age': 'Alter des Kindes',
        }

# FormSet для добавления нескольких детей (макс. 5 по умолчанию)
ChildFormSet = inlineformset_factory(
    Participant,
    Child,
    form=ChildForm,
    extra=0,  # не добавляет лишних пустых форм, только по факту
    can_delete=True,
)



class ParticipantProfileForm(forms.ModelForm):
    OVERNIGHT_CHOICES = [
        ('sat_sun', 'Sa - So'),
        ('sun_mon', 'So - Mo'),
        ('mon_tue', 'Mo - Di'),
        ('tue_wed', 'Di - Mi'),
        ('wed_thu', 'Mi - Do'),
        ('thu_fri', 'Do - Fr'),
        ('full_week', 'Vollzeit'),
    ]

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

    overnight_stays = forms.MultipleChoiceField(
        choices=OVERNIGHT_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Übernachten'
    )

    services = forms.MultipleChoiceField(
        choices=SERVICES_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label='Dienste'
    )

    class Meta:
        model = Participant
        fields = [
            'participation_type', 'first_name', 'last_name', 'is_student', 'age',
            'comes_with_partner', 'arrival_date', 'departure_date', 'overnight_stays',
            'family_members', 'has_children', 'number_of_children',
            'food_preference', 'has_dietary_restrictions', 'dietary_details',
            'services', 'leisure_activities',
            'street', 'street_extra', 'postal_code', 'city',
            'phone_number', 'email', 'church_contact',
            'comment', 'privacy_accepted'
        ]
        widgets = {
            'arrival_date': forms.DateInput(attrs={'type': 'date'}),
            'departure_date': forms.DateInput(attrs={'type': 'date'}),
            # 'children_ages': forms.TextInput(attrs={'placeholder': 'z. B. 5, 8'}),
            'dietary_details': forms.TextInput(attrs={'placeholder': 'z. B. Vegetarisch'}),
            'leisure_activities': forms.Textarea(attrs={'rows': 2}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'participation_type': 'Ich möchte',
            'first_name': 'Vorname',
            'last_name': 'Nachname',
            'is_student': 'Schüler/Azubi/Student',
            'age': 'Alter',
            'comes_with_partner': 'Komme mit Ehepartner',
            'family_members': 'Familienmitglieder',
            'has_children': 'Gibt es Kinder?',
            # 'children_ages': 'Alter der Kinder',
            'food_preference': 'Mittagessen',
            'has_dietary_restrictions': 'Gibt es Einschränkungen beim Essen?',
            'dietary_details': 'Welche?',
            'services': 'Dienste',
            'leisure_activities': 'Ich biete folgende Freizeit-Aktivitäten an',
            'street': 'Straße',
            'street_extra': 'Straße Zusatz',
            'postal_code': 'PLZ',
            'city': 'Ort',
            'phone_number': 'Handy-Nummer',
            'church_contact': 'Gemeinschaft oder Kontakt mit der Gemeinde in:',
            'comment': 'Bemerkungen',
            'privacy_accepted': 'Ich habe die Datenschutzerklärung gelesen und akzeptiert',
        }

def clean(self):
    cleaned_data = super().clean()
    # if cleaned_data.get('has_children') and not cleaned_data.get('children_ages'):
    #     self.add_error('children_ages', 'Bitte geben Sie das Alter der Kinder an.')
    if cleaned_data.get('has_dietary_restrictions') and not cleaned_data.get('dietary_details'):
        self.add_error('dietary_details', 'Bitte geben Sie Details zu den Ernährungseinschränkungen an.')
    if not cleaned_data.get('privacy_accepted'):
        self.add_error('privacy_accepted', 'Bitte akzeptieren Sie die Datenschutzerklärung.')