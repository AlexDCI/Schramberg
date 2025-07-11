from django.shortcuts import render, redirect, get_object_or_404
from .forms import ParticipantLoginForm, ParticipantProfileForm, ChildFormSet, ChildForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Participant, Child
from django.forms import inlineformset_factory

def staff_check(user):
    """Return True if the user is marked as staff."""
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
    """
    participant_id = request.session.get('participant_id')
    if not participant_id:
        return None
    return get_object_or_404(Participant, id=participant_id)

def get_num_children(request, participant):
    """
    Determines the intended number of children for the participant.
    Tries to get this from POST data; falls back to the participant's existing value.
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
    total_people = sum(p.family_members for p in participants)

    context = {
        'participants': participants,
        'total_people': total_people,
    }
    return render(request, 'users/dashboard.html', context)