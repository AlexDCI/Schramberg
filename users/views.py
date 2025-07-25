from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantLoginForm, ParticipantProfileForm, ChildFormSet, ChildForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Participant, Child
from django.forms import inlineformset_factory
from django.db.models import Sum
from collections import Counter
from django.contrib.auth.hashers import make_password, check_password
from django.db import IntegrityError

from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings
from .forms import ParticipantPasswordResetRequestForm
from .utils import generate_password_reset_token

from django.http import Http404
from .utils import verify_password_reset_token
from .forms import ParticipantSetNewPasswordForm
from .forms import ParticipantRegisterForm
from django.shortcuts import redirect



def participant_register(request):
    """
    Этап 1: базовая регистрация участника (имя, email, пароль).
    После регистрации — логин и редирект на форму профиля.
    """
    if request.method == 'POST':
        form = ParticipantRegisterForm(request.POST)
        if form.is_valid():
            participant = form.save()
            request.session['participant_id'] = participant.id
            return redirect('participant_profile')  # переход на анкету
    else:
        form = ParticipantRegisterForm()

    return render(request, 'users/registration.html', {'form': form})



def staff_check(user):
    """Return True if the user is marked as staff.
    Возвращает True, если пользователь отмечен как staff"""
    return user.is_staff

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
    """
    Удаляет participant_id из сессии и перенаправляет на страницу входа.
    """
    if 'participant_id' in request.session:
        del request.session['participant_id']
    return redirect('participant_login')  # или на 'start' страницу, если хочешь



def get_participant(request):
    """
    Retrieves the current participant object based on the session.
    Returns None if the participant is not found in the session.
    Получает объект участника на основе сессии.
    Возвращает None, если участник не найден в сессии.
    """
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return None
    return get_object_or_404(Participant, id=participant_id)

def get_num_children(request, participant):
    """
    Determines the intended number of children for the participant.
    Tries to get this from POST data; falls back to the participant's existing value.
    Определяет желаемое количество детей для участника.
    Сначала пытается получить из POST-данных, затем из существующего значения участника.
    """
    try:
        return int(request.POST.get('number_of_children', participant.number_of_children or 0))
    except (TypeError, ValueError):
        return participant.number_of_children or 0

def make_child_formset(participant, num_children, data=None):
    """
    Constructs a formset for the participant's children.
    - If data is provided (POST), binds the formset to the submitted data.
    - Otherwise, creates an unbound formset for rendering.
    - The number of extra forms is set so that the total matches num_children (at least 1 for new users).
    Создаёт formset для детей участника.
    - Если переданы данные (POST), связывает formset с этими данными.
    - Иначе создаёт несвязанный formset для отображения.
    - Количество дополнительных форм устанавливается так, чтобы всего было num_children (минимум 1 для новых пользователей).
    """
    extra = max(num_children - participant.children.count(), 1)
    ChildFormSetDynamic = inlineformset_factory(
        Participant,
        Child,
        form=ChildForm,
        extra=extra,
        can_delete=True,
    )
    if data:
        return ChildFormSetDynamic(data, instance=participant, prefix='children')
    return ChildFormSetDynamic(instance=participant, prefix='children')

def process_form_and_formset(form, formset, participant):
    """
    Обрабатывает сохранение участника и форм детей.
    - Сохраняет участника с обработкой возможной ошибки дублирования email.
    - Удаляет отмеченных детей.
    - Сохраняет остальные формы.
    - Обновляет количество детей у участника.
    Возвращает True, если всё успешно, иначе False.
    """
    try:
        participant = form.save(commit=False)
        participant.save()
    except IntegrityError:
        form.add_error('email', 'Diese Email-Adresse wird bereits verwendet.')
        return False  # Прерываем процесс при ошибке

    # Удаление отмеченных детей
    for child_form in formset.forms:
        if child_form.cleaned_data.get('DELETE', False) and child_form.instance.pk:
            child_form.instance.delete()

    # Сохраняем все формы
    formset.save()

    # Обновляем количество детей
    num_children = participant.children.count()
    participant.number_of_children = num_children
    participant.has_children = num_children > 0
    participant.save()

    return True

def participant_profile(request):
    """
    Обрабатывает отображение и отправку формы профиля участника.
    Добавлена проверка успешности сохранения (True/False).
    """
    participant = get_participant(request)
    if not participant:
        return redirect('participant_login')

    if request.method == 'POST':
        form = ParticipantProfileForm(request.POST, instance=participant)
        num_children = get_num_children(request, participant)

        if 'submit' not in request.POST:
            # Промежуточная отправка (например, при изменении количества детей)
            formset = make_child_formset(participant, num_children)
        else:
            # Окончательное сохранение
            formset = ChildFormSet(request.POST, instance=participant, prefix='children')
            if form.is_valid() and formset.is_valid():
                if process_form_and_formset(form, formset, participant):
                    return render(request, 'users/profile.html', {
                        'form': ParticipantProfileForm(instance=participant),
                        'formset': ChildFormSet(instance=participant, prefix='children'),
                        'success': True,
                    })
            else:
        # ❗ Показываем те же формы обратно с ошибками (например, дублирующийся email)
                return render(request, 'users/profile.html', {
                    'form': form,
                    'formset': formset,
                })
                # Если сохранение не удалось (например, email дублируется), остаёмся на форме
    else:
        # GET-запрос
        num_children = participant.number_of_children or 0
        form = ParticipantProfileForm(instance=participant)
        formset = make_child_formset(participant, num_children)

    return render(request, 'users/profile.html', {
        'form': form,
        'formset': formset,
    })




def nights(participant):
    """Calculate number of nights for a participant.
    Считает количество ночей для участника."""
    if participant.arrival_date and participant.departure_date:
        return (participant.departure_date - participant.arrival_date).days
    return 0

def get_kurtaxe_groups(participants):
    """Build Kurtaxe groups by age.
    Формирует группы для курортного сбора по возрасту."""
    adults, kids_10_17, kids_under_10 = [], [], []
    for p in participants:
        if p.age and p.age >= 18:
            adults.append({'nights': nights(p)})
        for c in p.children.all():
            if c.age >= 10 and c.age <= 17:
                kids_10_17.append({'nights': nights(p)})
            elif c.age < 10:
                kids_under_10.append({'nights': nights(p)})
    groups = [
        {'name': 'Erwachsene (18+)/ Взрослые (18+)', 'people': len(adults), 'nights': sum(a['nights'] for a in adults), 'kurtaxe_sum': round(len(adults) * 1.8 * sum(a['nights'] for a in adults), 2), 'discount': ''},
        {'name': 'Kinder 10-17/ Дети 10-17', 'people': len(kids_10_17), 'nights': sum(a['nights'] for a in kids_10_17), 'kurtaxe_sum': round(len(kids_10_17) * 1.0 * sum(a['nights'] for a in kids_10_17), 2), 'discount': ''},
        {'name': 'Kinder unter 10/ Дети до 10', 'people': len(kids_under_10), 'nights': sum(a['nights'] for a in kids_under_10), 'kurtaxe_sum': 0, 'discount': ''},
    ]
    total = sum(g['kurtaxe_sum'] for g in groups)
    return groups, total

def get_bed_list(participants):
    """Count bed linen sets for each group.
    Считает комплекты постельного белья для каждой группы."""
    bed_list = [{'group': p.full_name(), 'count': p.family_members} for p in participants]
    bed_total = sum(b['count'] for b in bed_list)
    return bed_list, bed_total

def get_email_list(participants):
    """Collect emails for mailing list.
    Собирает email-адреса для рассылки."""
    return [{'group': p.full_name(), 'address': p.email} for p in participants]

def get_payment_list(participants):
    """Build list of payments per participant.
    Формирует список взносов по каждому участнику."""
    return [{
        'name': p.full_name(),
        'email': p.email,
        'people': p.family_members,
        'nights': nights(p),
        'full_price': '',      # Fill if you have this field
        'partial_price': '',   # Fill if you have this field
        'total': '',           # Fill if you have this field
        'payment_method': '',  # Fill if you have this field
        'note': p.comment,
    } for p in participants]



def get_instrument_stats(participants):
    """
    Count musical instruments among participants.
    Считает музыкальные инструменты среди участников.
    """
    instrument_keywords = ['gitarre', 'klavier', 'schlagzeug', 'bass', 'gesang']
    instrument_stats = Counter()
    for p in participants:
        services = [s.strip().lower() for s in (p.services or '').split(',')]
        for s in services:
            if s in instrument_keywords:
                instrument_stats[s] += 1
    print('DEBUG instrument_stats:', instrument_stats, type(instrument_stats))  # <-- ОТЛАДКА
    return instrument_stats


def get_service_stats(participants):
    """
    Count services (volunteer roles) among participants.
    Считает служения среди участников.
    """
    instrument_keywords = ['gitarre', 'klavier', 'schlagzeug', 'bass', 'gesang']
    service_stats = Counter()
    for p in participants:
        services = [s.strip().lower() for s in (p.services or '').split(',')]
        for s in services:
            if s and s not in instrument_keywords:
                service_stats[s] += 1
    return service_stats

def get_food_stats(participants):
    """
    Count food preferences among participants.
    Считает типы питания среди участников.
    """
    food_stats = Counter()
    for p in participants:
        food_stats[(p.food_preference or 'unbekannt')] += 1
    return food_stats

def get_special_diets(participants):
    """
    List all individual dietary restrictions.
    Список индивидуальных ограничений по питанию.
    """
    special_diets = []
    for p in participants:
        if p.has_dietary_restrictions and p.dietary_details:
            special_diets.append({'name': p.full_name(), 'details': p.dietary_details})
    return special_diets

def get_important_notes(participants):
    """
    Collect all comments/important notes from participants.
    Собирает все комментарии/особые случаи от участников.
    """
    notes = []
    for p in participants:
        if p.comment:
            notes.append({'name': p.full_name(), 'note': p.comment})
    return notes

@login_required
@user_passes_test(staff_check)
def admin_dashboard(request):
    participants = Participant.objects.all()

    # Общая статистика / General statistics
    total_participants = participants.count()
    total_people = participants.aggregate(total=Sum('family_members'))['total'] or 0
    total_children = Child.objects.count()
    total_emails = participants.exclude(email='').count()

    # Улучшенные блоки
    instrument_stats = get_instrument_stats(participants)
    service_stats = get_service_stats(participants)
    food_stats = get_food_stats(participants)
    special_diets = get_special_diets(participants)
    important_notes = get_important_notes(participants)

    # Остальные блоки
    kurtaxe_groups, kurtaxe_total = get_kurtaxe_groups(participants)
    bed_list, bed_total = get_bed_list(participants)
    email_list = get_email_list(participants)
    payment_list = get_payment_list(participants)

    context = {
        'stats': {
            'total_participants': total_participants,
            'total_people': total_people,
            'total_children': total_children,
            'total_nights': sum(nights(p) for p in participants),
            'total_emails': total_emails,
        },
        'instrument_stats': dict(instrument_stats),
        'service_stats': dict(service_stats),
        'food_stats': dict(food_stats),
        'special_diets': special_diets,
        'important_notes': important_notes,
        'kurtaxe_groups': kurtaxe_groups,
        'kurtaxe_total': kurtaxe_total,
        'bed_list': bed_list,
        'bed_total': bed_total,
        'email_list': email_list,
        'payment_list': payment_list,
        'total_emails': total_emails,
    }
    return render(request, 'users/dashboard.html', context)


# block send email

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