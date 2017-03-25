from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from answers import models as answers_models
from core import models as core_models


@login_required(login_url='/hip-help/admin/login/')
def summary(request, room_name):
    room=get_object_or_404(core_models.Installation, room_name=room_name)
    rooms=core_models.Installation.objects.all()
    answers=answers_models.Answer.objects.filter(installation=room)
    return render(request, 'answers/summary.html', context={
        'answers':answers,
        'rooms':rooms
    })
