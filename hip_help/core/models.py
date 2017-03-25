import requests

from django.db import models
from django.db.models import Q

from . import views


class Installation(models.Model):
    oauth_id = models.CharField(max_length=100)
    capabilities_url = models.CharField(max_length=100)
    room_id = models.IntegerField()
    room_name = models.CharField(max_length=100)
    group_id = models.IntegerField()
    oauth_secret = models.CharField(max_length=100)

    authorization_url = models.URLField(blank=True)
    token_url = models.URLField(blank=True)
    api_url = models.URLField(blank=True)

    def find_match(self, sentence):
        query = Q()
        initial_queryset = self.answers.all()
        for word in sentence.split():
            query |= Q(keyword=word)
        queryset = initial_queryset.filter(query).distinct()
        return [q.keyword for q in queryset]

    def find_answer(self, keyword):
        try:
            return self.answers.get(keyword=keyword).text
        except models.ObjectDoesNotExist:
            pass

    def has_token(self):
        return AccessToken.objects.filter(installation=self).exists()

    def fetch_room_name(self):
        token = views.get_token(self)
        response = requests.get('/'.join([self.api_url, 'room', str(self.room_id)]), headers={
            'Authorization': 'Bearer ' + token.token
        })
        room = response.json()
        return room['name']

    def set_room_name(self):
        room_name = self.fetch_room_name()
        self.room_name = room_name
        self.save()

    def __str__(self):
        return str(self.room_id)


class AccessToken(models.Model):
    installation = models.OneToOneField('Installation')

    expiration_timestamp = models.DateTimeField()
    token = models.CharField(max_length=100)