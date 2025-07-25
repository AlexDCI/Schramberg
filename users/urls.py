from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('conference/', views.participant_login, name='participant_login'),  # Вход и регистрация
    path('logout/', views.participant_logout, name='participant_logout'),
    path('profile/', views.participant_profile, name='participant_profile'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('register/', views.participant_register, name='participant_register'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),

    # Password reset (Django built-in)
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),


    path('participant-password-reset/', views.participant_password_reset_request, name='participant_password_reset_request'),
    path('participant-password-reset/done/', views.participant_password_reset_done, name='participant_password_reset_done'),
    path('participant-password-reset-confirm/<str:token>/', views.participant_password_reset_confirm, name='participant_password_reset_confirm'),
    path('participant-password-reset-complete/', views.participant_password_reset_complete, name='participant_password_reset_complete'),
    
]
