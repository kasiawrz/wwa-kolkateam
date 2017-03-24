from django.db import models

from core.models import Installation


class Answer(models.Model):
    keyword = models.CharField(max_length=30)
    text = models.TextField()
    installation = models.ForeignKey('core.Installation', related_name='answers')
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    ask_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('installation', 'keyword')

    @classmethod
    def save_records(cls, records_dict):
        cls.objects.all().delete()
        room_name_set = set()
        for room_name, _ in records_dict:
            room_name_set.add(room_name)
        room_name_list = list(room_name_set)
        room_objects = Installation.objects.filter(group_id__in=int())


    def __str__(self):
        return self.keyword