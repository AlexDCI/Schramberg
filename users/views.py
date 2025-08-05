from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from django.http import Http404
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import messages


from .models import Participant, Registration, Adult, Child
from .forms import (
    ParticipantLoginForm,
    ParticipantRegisterForm,
    ParticipantPasswordResetRequestForm,
    ParticipantSetNewPasswordForm,
    RegistrationForm,
    AdultForm,
    ChildForm,
)
from .utils import generate_password_reset_token, verify_password_reset_token


def registration_edit(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id)
    # Тут можно добавить проверку, что request.user/participant владеет этим reg

    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            messages.success(request, "Änderungen gespeichert!")
            # Можно делать редирект на профиль или обратно к списку регистраций
            return redirect('participant_profile')
    else:
        form = RegistrationForm(instance=reg)

    adults = reg.adults.all()
    children = reg.children.all()

    return render(request, 'users/registration_edit.html', {
        'form': form,
        'reg': reg,
        'adults': adults,
        'children': children,
    })


def registration_delete(request, reg_id):
    reg = get_object_or_404(Registration, id=reg_id)
    # Проверка владельца, если надо!
    if request.method == "POST":
        reg.delete()
        messages.success(request, "Anmeldung wurde gelöscht!")
        return redirect('participant_profile')
    # Если через GET, можно просто подтвердить удаление
    return render(request, 'users/registration_confirm_delete.html', {'reg': reg})

def adult_edit(request, adult_id):
    adult = get_object_or_404(Adult, id=adult_id)
    reg = adult.registration
    participant = reg.participant
    # (Можно добавить проверку, что редактирует владелец)
    if request.method == 'POST':
        form = AdultForm(request.POST, instance=adult)
        if form.is_valid():
            form.save()
            return redirect('registration_edit', reg_id=reg.id)
    else:
        form = AdultForm(instance=adult)
    return render(request, 'users/registration_add_adult.html', {'form': form, 'edit_mode': True})


def adult_delete(request, adult_id):
    adult = get_object_or_404(Adult, id=adult_id)
    reg_id = adult.registration.id
    adult.delete()
    return redirect('registration_edit', reg_id=reg_id)

def child_edit(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    reg = child.registration
    participant = reg.participant
    if request.method == 'POST':
        form = ChildForm(request.POST, instance=child)
        if form.is_valid():
            form.save()
            return redirect('registration_edit', reg_id=reg.id)
    else:
        form = ChildForm(instance=child)
    return render(request, 'users/registration_add_child.html', {'form': form, 'edit_mode': True})


def child_delete(request, child_id):
    child = get_object_or_404(Child, id=child_id)
    reg_id = child.registration.id
    child.delete()
    return redirect('registration_edit', reg_id=reg_id)



# -------------- ПРОФИЛЬ УЧАСТНИКА ---------------

def participant_profile(request):
    participant = get_participant(request)
    if not participant:
        return redirect('participant_login')
    registrations = Registration.objects.filter(participant=participant)
    return render(request, 'users/participant_profile.html', {
        'participant': participant,
        'registrations': registrations,
    })

# ----------- МАСТЕР СОЗДАНИЯ АНМЕЛЬДУНГА -----------

def registration_start(request):
    participant = get_participant(request)
    if not participant:
        return redirect('participant_login')

    reg_id = request.session.get('reg_id')
    reg = None

    if reg_id:
        try:
            reg = Registration.objects.get(id=reg_id, participant=participant)
        except Registration.DoesNotExist:
            reg = None

    # Если регистрации нет — создаём новую!
    if not reg:
        reg = Registration.objects.create(participant=participant)
        request.session['reg_id'] = reg.id

    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            # Если ты хочешь, чтобы после завершения всё удалялось:
            del request.session['reg_id']
            return redirect('participant_profile')
    else:
        form = RegistrationForm(instance=reg)
    return render(request, 'users/registration_start.html', {
        'form': form,
        'reg': reg,
    })



def registration_add_adult(request):
    participant = get_participant(request)
    reg_id = request.session.get('reg_id')
    reg = get_object_or_404(Registration, id=reg_id, participant=participant)
    if request.method == 'POST':
        form = AdultForm(request.POST)
        if form.is_valid():
            adult = form.save(commit=False)
            adult.registration = reg
            adult.save()
            return redirect('registration_start')
        else:
            messages.error(request, "Bitte korrigieren Sie die Fehler im Formular.")
    else:
        form = AdultForm()
    return render(request, 'users/registration_add_adult.html', {'form': form})

def registration_add_child(request):
    participant = get_participant(request)
    reg_id = request.session.get('reg_id')
    reg = get_object_or_404(Registration, id=reg_id, participant=participant)
    if request.method == 'POST':
        form = ChildForm(request.POST)
        if form.is_valid():
            child = form.save(commit=False)
            child.registration = reg
            child.save()
            return redirect('registration_start')
    else:
        form = ChildForm()
    return render(request, 'users/registration_add_child.html', {'form': form})

def registration_overview(request):
    participant = get_participant(request)
    reg_id = request.session.get('reg_id')
    reg = get_object_or_404(Registration, id=reg_id, participant=participant)
    adults = reg.adults.all()
    children = reg.children.all()
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=reg)
        if form.is_valid():
            form.save()
            del request.session['reg_id']
            return redirect('participant_profile')
    else:
        form = RegistrationForm(instance=reg)
    return render(request, 'users/registration_overview.html', {
        'form': form,
        'reg': reg,
        'adults': adults,
        'children': children,
    })

# -------------- АВТОРИЗАЦИЯ/РЕГИСТРАЦИЯ -----------------

def participant_register(request):
    if request.method == 'POST':
        form = ParticipantRegisterForm(request.POST)
        if form.is_valid():
            participant = form.save()
            request.session['participant_id'] = participant.id
            return redirect('participant_profile')
    else:
        form = ParticipantRegisterForm()
    return render(request, 'users/registration.html', {'form': form})

def participant_login(request):
    if request.method == 'POST':
        form = ParticipantLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            raw_password = form.cleaned_data['password']
            try:
                participant = Participant.objects.get(email__iexact=email)
                if not check_password(raw_password, participant.password):
                    form.add_error('password', 'Falsches Passwort')
                else:
                    request.session['participant_id'] = participant.id
                    return redirect('participant_profile')
            except Participant.DoesNotExist:
                form.add_error('email', 'Kein Benutzer mit dieser Email gefunden.')
    else:
        form = ParticipantLoginForm()
    return render(request, 'users/start_login.html', {'form': form})

def participant_logout(request):
    if 'participant_id' in request.session:
        del request.session['participant_id']
    return redirect('participant_login')

def get_participant(request):
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return None
    return get_object_or_404(Participant, id=participant_id)

# ------------- PASSWORD RESET (как у тебя было) -------------

def participant_password_reset_request(request):
    if request.method == "POST":
        form = ParticipantPasswordResetRequestForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            token = generate_password_reset_token(email)
            reset_url = request.build_absolute_uri(
                reverse('participant_password_reset_confirm', args=[token])
            )
            send_mail(
                subject="Сброс пароля",
                message=f"Перейдите по ссылке, чтобы сбросить пароль:\n{reset_url}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
            )
            return redirect('participant_password_reset_done')
    else:
        form = ParticipantPasswordResetRequestForm()
    return render(request, 'users/participant_password_reset_request.html', {'form': form})

def participant_password_reset_confirm(request, token):
    email = verify_password_reset_token(token)
    if email is None:
        raise Http404("Неверный или просроченный токен.")
    participant = Participant.objects.filter(email=email).first()
    if not participant:
        raise Http404("Участник не найден.")
    if request.method == "POST":
        form = ParticipantSetNewPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password1']
            participant.set_password(new_password)
            participant.save()
            return redirect('participant_login')
    else:
        form = ParticipantSetNewPasswordForm()
    return render(request, 'users/participant_password_reset_confirm.html', {'form': form})

def participant_password_reset_done(request):
    return render(request, 'users/participant_password_reset_done.html')

def participant_password_reset_complete(request):
    return render(request, 'users/participant_password_reset_complete.html')

def privacy_policy(request):
    return render(request, 'users/privacy_policy.html')
