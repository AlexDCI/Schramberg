from django.contrib.auth.hashers import make_password, check_password
from django.db import models


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

    participation_type = models.CharField(max_length=20, choices=[('onsite', 'Vor Ort'), ('online', 'Nur Online')])
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    overnight_stays = models.CharField(max_length=100, blank=True)

    is_student = models.BooleanField(default=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    comes_with_partner = models.BooleanField(default=False)
    family_members = models.PositiveIntegerField(default=1)

    food_preference = models.CharField(max_length=20, choices=[
        ('normal', 'Normal'),
        ('vegetarian', 'Vegetarisch'),
        ('lactose_free', 'Laktosefrei')
    ])
    has_children = models.BooleanField(default=False)
    number_of_children = models.PositiveIntegerField(default=0)

    services = models.CharField(max_length=200, blank=True)
    leisure_activities = models.TextField(blank=True)

    church_contact = models.CharField(max_length=200, blank=True)
    needs_transport = models.BooleanField(default=False)
    has_dietary_restrictions = models.BooleanField(default=False)
    dietary_details = models.CharField(max_length=200, blank=True)

    comment = models.TextField(blank=True)

    def __str__(self):
        return f"Anmeldung von {self.participant.full_name()} ({self.arrival_date})"



class Child(models.Model):
    registration = models.ForeignKey(Registration, on_delete=models.CASCADE, related_name='children')
    name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.name} ({self.age})'


