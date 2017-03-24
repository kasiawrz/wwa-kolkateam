import requests
import json

from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse
from django.conf import settings

from . import models as core_models


@require_GET
@csrf_exempt
def capabilities(request):
    capabilities_data = settings.GET_CAPABILITIES(reverse('help'), reverse('capabilities'),
                                             reverse('installed'))

    return JsonResponse(capabilities_data)


@require_POST
@csrf_exempt
def installed(request):
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

    return HttpResponse(status=200)


def help(request):
    pass