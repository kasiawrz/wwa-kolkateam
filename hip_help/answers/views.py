from django.shortcuts import render
from answers import models as answers_models
from core import models as core_models


def summary(request, room_name):
    room=core_models.Installation.objects.get(room_name=room_name)
    rooms=core_models.Installation.objects.all()
    answers=answers_models.Answer.objects.filter(installation=room)
    return render(request, 'answers/summary.html', context={
        'answers':answers,
        'rooms':rooms
    })
