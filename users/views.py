from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantLoginForm, ParticipantProfileForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Participant

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
        if form.is_valid():
            form.save()
            return render(request, 'users/profile.html', {'form': form, 'success': True})
    else:
        form = ParticipantProfileForm(instance=participant)

    return render(request, 'users/profile.html', {'form': form})



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