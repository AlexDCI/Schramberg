from django.contrib.auth.hashers import make_password, check_password
from django.db import models
from django.utils import timezone


class Participant(models.Model):
    # 🔐 Только данные регистрации / логина
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    street_extra = models.CharField(max_length=100, blank=True)
    
    # ✅ Обязательное согласие
    privacy_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.password)


class Registration(models.Model):
    participant = models.ForeignKey(Participant, on_delete=models.CASCADE, related_name='registrations')
    # Общие для всех участников этой регистрации:
    leisure_activities = models.TextField(blank=True)
    church_contact = models.CharField(max_length=200, blank=True)
    needs_transport = models.BooleanField(default=False)
    has_dietary_restrictions = models.BooleanField(default=False)
    dietary_details = models.CharField(max_length=200, blank=True)
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Anmeldung von {self.participant.full_name()} ({self.id})"


class Adult(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('male', 'Männlich'),
        ('female', 'Weiblich'),
    ]
    
    HOUSING_CHOICES = [
        ('family', 'Mit Familie im eigenen Haus'),
        ('brudershaus', 'Brüderhaus (für Männer)'),
        ('sisterhaus', 'Schwesterhaus (für Frauen)'),
        ('no_preference', 'Keine Präferenz'),
    ]

    registration = models.ForeignKey('Registration', on_delete=models.CASCADE, related_name='adults')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male',)
    housing_preference = models.CharField(
        max_length=20,
        choices=HOUSING_CHOICES,
        default='family',
        blank=True
    )
    participation_type = models.CharField(max_length=20, choices=[('onsite', 'Vor Ort'), ('online', 'Nur Online')], default='onsite',)
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    is_full_week = models.BooleanField(
        default=False,
        verbose_name="Vollzeit (полное время)"
    )
    is_student = models.BooleanField(default=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    comes_with_partner = models.BooleanField(default=False)
    food_preference = models.CharField(
        max_length=20,
        choices=[('normal', 'Normal'), ('vegetarian', 'Vegetarisch')],
        default='normal'  # <= вот так!
        )
    
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
    services = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.age} J. ({self.participation_type})"
    
    @property
    def services_list(self):
        # Разбивает строку "guitar,piano" → ["guitar", "piano"]
        return [s for s in self.services.split(',') if s.strip()]


class Child(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    GENDER_CHOICES = [
        ('male', 'Junge'),
        ('female', 'Mädchen'),
    ]
    HOUSING_CHOICES = [
        ('family', 'Mit Familie im eigenen Haus'),
        ('brudershaus', 'Brüderhaus (für Jungen)'),
        ('sisterhaus', 'Schwesterhaus (für Mädchen)'),
        ('no_preference', 'Keine Präferenz'),
    ]

    registration = models.ForeignKey('Registration', on_delete=models.CASCADE, related_name='children')
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default='male',)
    housing_preference = models.CharField(
        max_length=20,
        choices=HOUSING_CHOICES,
        default='family',
        blank=True
    )
    participation_type = models.CharField(max_length=20, choices=[('onsite', 'Vor Ort'), ('online', 'Nur Online')], default='onsite',)
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    is_full_week = models.BooleanField(
        default=False,
        verbose_name="Vollzeit (полное время)"
    )
    is_student = models.BooleanField(default=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    food_preference = models.CharField(
        max_length=20,
        choices=[('normal', 'Normal'), ('vegetarian', 'Vegetarisch')],
        default='normal'  # <= вот так!
        )
    
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
    services = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.age} J. ({self.participation_type})"
    
    @property
    def services_list(self):
        # Разбивает строку "guitar,piano" → ["guitar", "piano"]
        return [s for s in self.services.split(',') if s.strip()]
