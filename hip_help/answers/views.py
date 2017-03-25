from django.shortcuts import render
from answers import models as answers_models
from core import models as core_models


def summary(request, id):
    room=core_models.Installation.objects.get(room_id=id)
    rooms=core_models.Installation.objects.all()
    answers=answers_models.Answer.objects.filter(installation=room)
    return render(request, 'answers/summary.html', context={
        'answers':answers,
        'rooms':rooms
    })
