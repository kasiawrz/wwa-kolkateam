import requests
import datetime
import json

from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.utils import timezone

from . import models as core_models


@require_GET
@csrf_exempt
def capabilities(request):
    capabilities_data = settings.GET_CAPABILITIES(
        reverse('help'), reverse('capabilities'),
        reverse('installed'), reverse('listener')
    )

    return JsonResponse(capabilities_data, status=200)


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


# todo move to model
def refresh_token(installation):
    # sets new token to installation and returns it
    if installation.has_token():
        installation.accesstoken.delete()

    auth = {
        'username': installation.oauth_id,
        'password': installation.oauth_secret
    }
    data = {
        'grant_type': 'client_credentials'
    }

    url = installation.token_url
    response = requests.post(url, data, auth=(auth['username'], auth['password']))
    token = response.json()

    token_object = core_models.AccessToken.objects.create(
        installation=installation,
        token=token['access_token'],
        expiration_timestamp=timezone.now() + datetime.timedelta(seconds=int(token['expires_in']))
    )

    return token_object


@require_POST
@csrf_exempt
def listener(request):
    message = json.loads(request.body.decode('utf-8'))
    room_id = message['item']['room']['id']

    keyword = message['item']['message']['message']
    keyword = " ".join(keyword.split()[1:])

    installation = core_models.Installation.objects.get(room_id=room_id)
    answer = installation.find_answer(keyword)

    if answer is not None:
        send_message(answer, installation)
    else:
        send_message('help message for "{keyword}" not found'.format(keyword=keyword), installation)

    return HttpResponse(status=204)


def send_message(message, installation):
    token = get_token(installation)
    notification_url = installation.api_url + 'room/' + str(installation.room_id) + '/notification'
    response = requests.post(
        url=notification_url,
        headers={
            'Authorization': 'Bearer ' + token.token
        },
        data={
            'message_format': 'text',
            'message': message,
            'notify': False,
            'color': 'gray'
        }
    )

#todo test
# todo move to model
def is_expired(token):
    return timezone.now() > token.expiration_timestamp


# todo move to model
def get_token(installation):
    if not installation.has_token() or is_expired(installation.accesstoken):  # checking if installation has token
        return refresh_token(installation)
    else:
        return installation.accesstoken


def help(request):
    pass