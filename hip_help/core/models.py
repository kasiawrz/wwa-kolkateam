from django.db import models


class Installation(models.Model):
    oauth_id = models.CharField(max_length=100)
    capabilities_url = models.CharField(max_length=100)
    room_id = models.IntegerField()
    group_id = models.IntegerField()
    oauth_secret = models.CharField(max_length=100)

    authorization_url = models.URLField(blank=True)
    token_url = models.URLField(blank=True)
    api_url = models.URLField(blank=True)

    def has_token(self):
        return AccessToken.objects.filter(installation=self).exists()


class AccessToken(models.Model):
    installation = models.OneToOneField('Installation')

    expiration_timestamp = models.DateTimeField()
    token = models.CharField(max_length=100)