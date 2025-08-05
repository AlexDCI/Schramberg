from .models import Participant

def current_participant(request):
    participant = None
    pid = request.session.get('participant_id')
    if pid:
        try:
            participant = Participant.objects.get(id=pid)
        except Participant.DoesNotExist:
            participant = None
    return {'current_participant': participant}