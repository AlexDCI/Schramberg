# Generated by Django 5.2.4 on 2025-07-14 10:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_participant_number_of_children'),
    ]

    operations = [
        migrations.AddField(
            model_name='participant',
            name='password',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
