from django.contrib import admin
from .models import Participant, Registration, Adult, Child

admin.site.register(Participant)
admin.site.register(Registration)
admin.site.register(Adult)
admin.site.register(Child)