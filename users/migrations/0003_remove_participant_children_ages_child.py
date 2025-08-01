# Generated by Django 5.2.4 on 2025-07-10 10:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_alter_participant_age'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='participant',
            name='children_ages',
        ),
        migrations.CreateModel(
            name='Child',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('age', models.PositiveIntegerField()),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='children', to='users.participant')),
            ],
        ),
    ]
