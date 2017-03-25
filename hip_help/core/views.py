import requests
import json

from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.conf import settings

from . import models as core_models


@require_GET
@csrf_exempt
def capabilities(request):
    capabilities_data = settings.GET_CAPABILITIES(
        reverse_lazy('help'), reverse_lazy('capabilities'),
        reverse_lazy('installed'), reverse_lazy('listener'), reverse_lazy('uninstalled')
    )
    return JsonResponse(capabilities_data, status=200)


@csrf_exempt
def installed(request):
    if request.method == 'DELETE':
        return HttpResponse(status=200)
    elif not request.body:
        redirect_url = request.GET.get('redirect_url', None)
        installable_url = request.GET.get('installable_url', None)
        response = requests.get(installable_url)
        installation = response.json()
        core_models.Installation.objects.get(oauth_id=installation['oauthId']).delete()
        return HttpResponseRedirect(redirect_url)

    installation_data = json.loads(request.body.decode('utf-8'))
    installation = core_models.Installation(
        oauth_id=installation_data['oauthId'],
        capabilities_url=installation_data['capabilitiesUrl'],
        room_id=installation_data['roomId'],
        group_id=installation_data['groupId'],
        oauth_secret=installation_data['oauthSecret']
    )

    response = requests.get(installation_data['capabilitiesUrl'])
    capabilities_data = response.json()
    installation.authorization_url = capabilities_data['capabilities']['oauth2Provider']['authorizationUrl']
    installation.token_url = capabilities_data['capabilities']['oauth2Provider']['tokenUrl']
    installation.api_url = capabilities_data['capabilities']['hipchatApiProvider']['url']
    installation.save()

    installation.set_room_name()
    installation.save()

    return HttpResponse(status=200)


@csrf_exempt
def uninstalled(request):
    redirect_url = request.GET.get('redirect_url', None)
    installable_url = request.GET.get('installable_url', None)
    response = requests.get(installable_url)
    installation = response.json()
    core_models.Installation.objects.get(oauth_id=installation['oauthId']).delete()
    return HttpResponseRedirect(redirect_url)


@require_POST
@csrf_exempt
def listener(request):
    message = json.loads(request.body.decode('utf-8'))
    room_id = message['item']['room']['id']

    keyword = message['item']['message']['message']
    installation = core_models.Installation.objects.get(room_id=room_id)

    if keyword.split()[0] == '/helpme':  # obligated to answer
        keywords = keyword.split()[1:]
        return help_me(keywords, installation)
    else:  # may answer
        suggestion = installation.make_suggestion(keyword)
        if suggestion is not None:
            installation.send_message('do you want information about {suggestion}? write /helpme {suggestion}'.format(suggestion=suggestion.keyword))

        return HttpResponse(status=204)


def help_me(keywords, installation):
    if len(keywords) > 1 and keywords[0] == 'like':
        keyword = ' '.join(keywords[1:])
        answer = installation.find_answer(keyword)  # everything except "like"

        if answer is not None:
            answer.like()
            installation.send_message('you liked "{keyword}"'.format(keyword=keyword))
        else:
            installation.send_message('"{keyword}" not found'.format(keyword=keyword))

    elif len(keywords) > 1 and keywords[0] == 'dislike':
        keyword = ' '.join(keywords[1:])
        answer = installation.find_answer(keyword)  # everything except "dislike"

        if answer is not None:
            answer.dislike()
            installation.send_message('you disliked "{keyword}"'.format(keyword=keyword))
        else:
            installation.send_message('"{keyword}" not found'.format(keyword=keyword))
    else:
        keyword = ' '.join(keywords)
        answer = installation.find_answer(keyword)
        if answer is not None:
            installation.send_message(answer.text)
        else:
            installation.send_message('help message for "{keyword}" not found'.format(keyword=keyword))

    if answer:
        answer.increment_ask_counter()

    return HttpResponse(status=204)


@login_required(login_url='/hip-help/admin/login/')
def home(request):
    room = core_models.Installation.objects.first()
    if not room:
        return HttpResponse('<h1>No rooms stats</h1>')
    return HttpResponseRedirect(reverse_lazy('summary', args=(room.room_name,)))


def help(request):
    return HttpResponse('Help')