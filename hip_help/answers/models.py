from django.db import models
from django.db.models import Q


class Answer(models.Model):
    keyword = models.CharField(max_length=30, unique=True)
    text = models.TextField()
    installation = models.ForeignKey('core.Installation')

    def __str__(self):
        return self.keyword

    @classmethod
    def find_match(cls, sentence):
        query = Q()
        for word in sentence.split():
            query |= Q(keyword=word)
        queryset = cls.objects.filter(query).distinct()
        return [q.keyword for q in queryset]