from django.db import models


# class Participant(models.Model):
#     full_name = models.CharField(max_length=100)
#     email = models.EmailField(unique=True)  # email уникален
#     family_members = models.PositiveIntegerField(default=1)
#     arrival_date = models.DateField(null=True, blank=True)
#     departure_date = models.DateField(null=True, blank=True)

#     def __str__(self):
#         return f'{self.full_name} ({self.email})'
class Participant(models.Model):
    # Основные данные
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    street = models.CharField(max_length=100)
    street_extra = models.CharField(max_length=100, blank=True)

    # Участие и проживание
    participation_type = models.CharField(max_length=20, choices=[('onsite', 'Vor Ort'), ('online', 'Nur Online')])
    arrival_date = models.DateField(null=True, blank=True)
    departure_date = models.DateField(null=True, blank=True)
    overnight_stays = models.CharField(max_length=100, blank=True)  # Пример: "Sa-So, Mo-Di"

    # Дополнительно
    is_student = models.BooleanField(default=False)
    age = models.PositiveIntegerField(null=True, blank=True)
    comes_with_partner = models.BooleanField(default=False)
    family_members = models.PositiveIntegerField(default=1)

    # Питание
    food_preference = models.CharField(max_length=20, choices=[
        ('normal', 'Normal'),
        ('vegetarian', 'Vegetarisch'),
        ('lactose_free', 'Laktosefrei')
    ])

    # Дети
    has_children = models.BooleanField(default=False)
    children_ages = models.CharField(max_length=100, blank=True)

    # Служения (могут быть множественные)
    services = models.CharField(max_length=200, blank=True)  # Можно хранить список как строку

    # Внепрограммная активность
    leisure_activities = models.TextField(blank=True)

    # Связь с общиной
    church_contact = models.CharField(max_length=200, blank=True)

    # Транспорт, питание
    needs_transport = models.BooleanField(default=False)
    has_dietary_restrictions = models.BooleanField(default=False)
    dietary_details = models.CharField(max_length=200, blank=True)

    # Комментарий
    comment = models.TextField(blank=True)

    # Согласие с политикой
    privacy_accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name} ({self.email})'
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"