from django.shortcuts import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from django.conf import settings


@require_GET
@csrf_exempt
def capabilities(request):
    return settings.GET_CAPABILITIES(reverse('help'), reverse('capabilities'),
                                     reverse('installed'))