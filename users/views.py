from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantLoginForm, ParticipantProfileForm, ChildFormSet, ChildForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Participant, Child
from django.forms import inlineformset_factory

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




def participant_profile(request):
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return redirect('participant_login')
    participant = get_object_or_404(Participant, id=participant_id)

    if request.method == 'POST':
        form = ParticipantProfileForm(request.POST, instance=participant)
        try:
            num_children = int(request.POST.get('number_of_children', 0))
        except (TypeError, ValueError):
            num_children = 0

        # Если это не финальный submit, а просто изменение количества детей — пересоздаём formset с нужным extra
        if 'submit' not in request.POST:
            ChildFormSetDynamic = inlineformset_factory(
                Participant,
                Child,
                form=ChildForm,
                extra=max(num_children - participant.children.count(), 1),  # всегда хотя бы 1
                can_delete=True,
            )
            formset = ChildFormSetDynamic(instance=participant, prefix='children')
        else:
            formset = ChildFormSet(request.POST, instance=participant, prefix='children')
            if form.is_valid() and formset.is_valid():
                participant = form.save(commit=False)
                participant.save()
                # Явное удаление детей
                for child_form in formset.forms:
                    if child_form.cleaned_data.get('DELETE', False) and child_form.instance.pk:
                        child_form.instance.delete()
                formset.save()
                # Пересчитываем количество детей
                num_children = participant.children.count()
                participant.number_of_children = num_children
                participant.has_children = num_children > 0
                participant.save()
                return render(request, 'users/profile.html', {
                    'form': ParticipantProfileForm(instance=participant),
                    'formset': ChildFormSet(instance=participant, prefix='children'),
                    'success': True,
                })
    else:
        # GET-запрос: всегда хотя бы одна форма для ребёнка
        num_children = participant.number_of_children or 0
        extra = max(num_children - participant.children.count(), 1)
        ChildFormSetDynamic = inlineformset_factory(
            Participant,
            Child,
            form=ChildForm,
            extra=extra,
            can_delete=True,
        )
        form = ParticipantProfileForm(instance=participant)
        formset = ChildFormSetDynamic(instance=participant, prefix='children')

    return render(request, 'users/profile.html', {
        'form': form,
        'formset': formset,
    })

def staff_check(user):
    return user.is_staff  # или user.is_superuser, если хочешь строже

@login_required
@user_passes_test(staff_check)
def admin_dashboard(request):
    participants = Participant.objects.all()
    total_people = sum(p.family_members for p in participants)

    context = {
        'participants': participants,
        'total_people': total_people,
    }
    return render(request, 'users/dashboard.html', context)