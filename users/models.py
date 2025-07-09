from django.db import models


class Participant(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)  # email уникален
    family_members = models.PositiveIntegerField(default=1)
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f'{self.full_name} ({self.email})'
