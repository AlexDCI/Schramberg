from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantLoginForm, ParticipantProfileForm, ChildFormSet, ChildForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Participant, Child
from django.forms import inlineformset_factory
from django.db.models import Sum

def staff_check(user):
    """Return True if the user is marked as staff.
    Возвращает True, если пользователь отмечен как staff"""
    return user.is_staff

def participant_login(request):
    if request.method == 'POST':
        form = ParticipantLoginForm(request.POST)
        if form.is_valid():
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            email = form.cleaned_data['email']
            age = form.cleaned_data['age']

            participant, created = Participant.objects.get_or_create(
                email=email,
                defaults={'first_name': first_name, 'last_name': last_name}
            )

            # При необходимости обновить имя
            if not created and (participant.first_name != first_name or participant.last_name != last_name):
                participant.first_name = first_name
                participant.last_name = last_name
                participant.save()

            request.session['participant_id'] = participant.id
            return redirect('participant_profile')
    else:
        form = ParticipantLoginForm()

    return render(request, 'users/login.html', {'form': form})




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
    Handles saving the participant and all child forms.
    - Saves the participant.
    - Deletes any children marked for deletion.
    - Saves all valid child forms.
    - Updates the participant's number_of_children and has_children fields.
    Обрабатывает сохранение участника и всех форм детей.
    - Сохраняет участника.
    - Удаляет всех детей, отмеченных на удаление.
    - Сохраняет все валидные формы детей.
    - Обновляет поля number_of_children и has_children у участника.
    """
    participant = form.save(commit=False)
    participant.save()
    for child_form in formset.forms:
        if child_form.cleaned_data.get('DELETE', False) and child_form.instance.pk:
            child_form.instance.delete()
    formset.save()
    num_children = participant.children.count()
    participant.number_of_children = num_children
    participant.has_children = num_children > 0
    participant.save()

def participant_profile(request):
    """
    Main view for handling participant profile display and submission.
    Splits logic for GET and POST requests and delegates to helper functions.
    Handles:
      - Rendering the profile form and dynamic number of child forms
      - Processing form submissions and saving/deleting children
      - Ensuring that at least one child form is available for new users
      Основная view-функция для отображения и обработки профиля участника.
    Разделяет логику для GET и POST-запросов и делегирует работу вспомогательным функциям.
    Обеспечивает:
      - Отображение формы профиля и динамического количества форм для детей
      - Обработку отправки формы и сохранение/удаление детей
      - Гарантирует, что для новых пользователей всегда есть хотя бы одна форма для ребёнка
    """
    participant = get_participant(request)
    if not participant:
        return redirect('participant_login')

    if request.method == 'POST':
        form = ParticipantProfileForm(request.POST, instance=participant)
        num_children = get_num_children(request, participant)

        # If this is not the final submit, re-render with new number of child forms
        if 'submit' not in request.POST:
            formset = make_child_formset(participant, num_children)
        else:
            formset = ChildFormSet(request.POST, instance=participant, prefix='children')
            if form.is_valid() and formset.is_valid():
                process_form_and_formset(form, formset, participant)
                return render(request, 'users/profile.html', {
                    'form': ParticipantProfileForm(instance=participant),
                    'formset': ChildFormSet(instance=participant, prefix='children'),
                    'success': True,
                })
    else:
        # GET request: always show at least one child form for new users
        num_children = participant.number_of_children or 0
        form = ParticipantProfileForm(instance=participant)
        formset = make_child_formset(participant, num_children)

    return render(request, 'users/profile.html', {
        'form': form,
        'formset': formset,
    })

@login_required
@user_passes_test(staff_check)
def admin_dashboard(request):
    participants = Participant.objects.all()

    # Общая статистика
    total_participants = participants.count()
    total_people = participants.aggregate(total=Sum('family_members'))['total'] or 0
    total_children = Child.objects.count()
    total_emails = participants.exclude(email='').count()

    # Считаем ночи для каждого участника
    def nights(p):
        if p.arrival_date and p.departure_date:
            return (p.departure_date - p.arrival_date).days
        return 0

    # Kurtaxe: разбивка по возрасту
    adults = []
    kids_10_17 = []
    kids_under_10 = []

    for p in participants:
        # Взрослый
        if p.age and p.age >= 18:
            adults.append({'nights': nights(p)})
        # Дети у участника
        for c in p.children.all():
            if c.age >= 10 and c.age <= 17:
                kids_10_17.append({'nights': nights(p)})
            elif c.age < 10:
                kids_under_10.append({'nights': nights(p)})

    kurtaxe_groups = [
        {'name': 'Erwachsene (18+)/ Взрослые (18+)', 'people': len(adults), 'nights': sum(a['nights'] for a in adults), 'kurtaxe_sum': round(len(adults) * 1.8 * sum(a['nights'] for a in adults), 2), 'discount': ''},
        {'name': 'Kinder 10-17/ Дети 10-17', 'people': len(kids_10_17), 'nights': sum(a['nights'] for a in kids_10_17), 'kurtaxe_sum': round(len(kids_10_17) * 1.0 * sum(a['nights'] for a in kids_10_17), 2), 'discount': ''},
        {'name': 'Kinder unter 10/ Дети до 10', 'people': len(kids_under_10), 'nights': sum(a['nights'] for a in kids_under_10), 'kurtaxe_sum': 0, 'discount': ''},
    ]
    kurtaxe_total = sum(g['kurtaxe_sum'] for g in kurtaxe_groups)

    # Постельное бельё (Bettwäsche) — пример: считаем по количеству family_members
    bed_list = []
    for p in participants:
        bed_list.append({'group': p.full_name(), 'count': p.family_members})
    bed_total = sum(b['count'] for b in bed_list)

    # Email-рассылка
    email_list = []
    for p in participants:
        email_list.append({'group': p.full_name(), 'address': p.email})

    # Взносы участников (пример, если есть поля для оплаты)
    payment_list = []
    for p in participants:
        payment_list.append({
            'name': p.full_name(),
            'email': p.email,
            'people': p.family_members,
            'nights': nights(p),
            'full_price': '',  # Заполните, если есть поле
            'partial_price': '',  # Заполните, если есть поле
            'total': '',  # Заполните, если есть поле
            'payment_method': '',  # Заполните, если есть поле
            'note': p.comment,
        })

    context = {
        'stats': {
            'total_participants': total_participants,
            'total_people': total_people,
            'total_children': total_children,
            'total_nights': sum(nights(p) for p in participants),
            'total_emails': total_emails,
        },
        'kurtaxe_groups': kurtaxe_groups,
        'kurtaxe_total': kurtaxe_total,
        'bed_list': bed_list,
        'bed_total': bed_total,
        'email_list': email_list,
        'payment_list': payment_list,
        'total_emails': total_emails,
    }
    return render(request, 'users/dashboard.html', context)