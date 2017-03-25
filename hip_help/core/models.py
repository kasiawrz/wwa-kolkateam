import datetime

import nltk
import requests

from django.db import models
from django.db.models import Q
from django.utils import timezone
from textblob import TextBlob


class Installation(models.Model):
    oauth_id = models.CharField(max_length=100, unique=True)
    capabilities_url = models.CharField(max_length=100)
    room_id = models.IntegerField(unique=True)
    room_name = models.CharField(max_length=100, unique=True)
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
            return self.answers.get(keyword=keyword)
        except models.ObjectDoesNotExist:
            pass

    def make_suggestion(self, sentence):
        grammar = "NP: {<JJ>*<NN>+}"
        text = TextBlob(sentence)
        cp = nltk.RegexpParser(grammar)
        candidates = []
        for item in cp.parse(text.tags):
            self.traverse_nltk_item(item, candidates)
        print(candidates)
        candidate_answers = self.answers.filter(keyword__in=candidates)
        if candidate_answers.exists():
            most_asked = candidate_answers.order_by('-ask_count').first()
        else:
            most_asked = None

        return most_asked

    def traverse_nltk_item(self, item, candidates):
        if isinstance(item, list):
            for nested_item in item:
                self.traverse_nltk_item(nested_item, candidates)
        elif isinstance(item, tuple):
            word, kind = item
            if kind in ['NN', 'NNP']:
                candidates.append(word)
        elif isinstance(item, nltk.tree.Tree):
            self.traverse_nltk_item(item, candidates)






    def has_token(self):
        return AccessToken.objects.filter(installation=self).exists()

    def fetch_room_name(self):
        token = self.get_token()
        response = requests.get('/'.join([self.api_url, 'room', str(self.room_id)]), headers={
            'Authorization': 'Bearer ' + token.token
        })
        room = response.json()
        print(room)
        return room['name']

    def set_room_name(self):
        room_name = self.fetch_room_name()
        self.room_name = room_name
        self.save()

    def get_token(self):
        if not self.has_token() or self.accesstoken.is_expired():  # checking if installation has token
            return self.refresh_token()
        else:
            return self.accesstoken

    def refresh_token(self):
        # sets new token to installation and returns it
        if self.has_token():
            self.accesstoken.delete()

        auth = {
            'username': self.oauth_id,
            'password': self.oauth_secret
        }
        data = {
            'grant_type': 'client_credentials'
        }

        url = self.token_url
        response = requests.post(url, data, auth=(auth['username'], auth['password']))
        token = response.json()

        token_object = AccessToken.objects.create(
            installation=self,
            token=token['access_token'],
            expiration_timestamp=timezone.now() + datetime.timedelta(seconds=int(token['expires_in']))
        )

        return token_object

    def send_message(self, message):
        token = self.get_token()
        notification_url = self.api_url + 'room/' + str(self.room_id) + '/notification'
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

    def __str__(self):
        return str(self.room_name)


class AccessToken(models.Model):
    installation = models.OneToOneField('Installation')

    expiration_timestamp = models.DateTimeField()
    token = models.CharField(max_length=100)

    def is_expired(self):
        return timezone.now() > self.expiration_timestamp