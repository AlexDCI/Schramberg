from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ----------- Авторизация/регистрация ----------
    path('conference/', views.participant_login, name='participant_login'),
    path('logout/', views.participant_logout, name='participant_logout'),
    path('register/', views.participant_register, name='participant_register'),
    path('privacy/', views.privacy_policy, name='privacy_policy'),
    path('registrierung/', views.participant_register, name='participant_register'),  # дублирует register/ — можно оставить для SEO/перевода

    # --------------- Профиль пользователя -------------
    path('profil/', views.participant_profile, name='participant_profile'),

    # ----------- Новый мастер создания анмельдунга ---------
    path('anmeldung/neu/', views.registration_start, name='registration_start'),                  # шаг 1
    path('anmeldung/neu/erwachsener/', views.registration_add_adult, name='registration_add_adult'),  # шаг 2
    path('anmeldung/neu/kind/', views.registration_add_child, name='registration_add_child'),         # шаг 3
    path('anmeldung/neu/abschluss/', views.registration_overview, name='registration_overview'),      # шаг 4


    # Для редактирования и удаления Anmeldung (анмельдунга)
    path('anmeldung/<int:reg_id>/bearbeiten/', views.registration_edit, name='registration_edit'),
    path('anmeldung/<int:reg_id>/loeschen/', views.registration_delete, name='registration_delete'),

    # Для взрослых
    path('erwachsener/<int:adult_id>/bearbeiten/', views.adult_edit, name='edit_adult'),
    path('erwachsener/<int:adult_id>/loeschen/', views.adult_delete, name='delete_adult'),

    # Для детей
    path('kind/<int:child_id>/bearbeiten/', views.child_edit, name='edit_child'),
    path('kind/<int:child_id>/loeschen/', views.child_delete, name='delete_child'),


    # ------------ (Оставь редактирование, если потребуется) ------------
    # path('anmeldung/<int:registration_id>/bearbeiten/', views.registration_edit, name='registration_edit'),
    # path('anmeldung/<int:registration_id>/loeschen/', views.registration_delete, name='registration_delete'),

    # --------------- Password reset (Django built-in) ----------------
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='users/password_reset.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='users/password_reset_done.html'), name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='users/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset-complete/', auth_views.PasswordResetCompleteView.as_view(template_name='users/password_reset_complete.html'), name='password_reset_complete'),

    # --------------- Custom password reset для участников -------------
    path('participant-password-reset/', views.participant_password_reset_request, name='participant_password_reset_request'),
    path('participant-password-reset/done/', views.participant_password_reset_done, name='participant_password_reset_done'),
    path('participant-password-reset-confirm/<str:token>/', views.participant_password_reset_confirm, name='participant_password_reset_confirm'),
    path('participant-password-reset-complete/', views.participant_password_reset_complete, name='participant_password_reset_complete'),
]
