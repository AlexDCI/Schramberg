from django.contrib import admin

from .models import Participant

@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'family_members', 'arrival_date', 'departure_date')
    search_fields = ('full_name', 'email')
