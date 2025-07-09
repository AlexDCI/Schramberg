from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.participant_login, name='participant_login'),  # Вход и регистрация
    path('profile/', views.participant_profile, name='participant_profile'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
]
