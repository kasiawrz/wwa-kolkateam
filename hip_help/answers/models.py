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
    #
    # @classmethod
    # def save_records(cls, records_dict):
    #     cls.objects.all().delete()
    #     room_name_set = set()
    #     for room_name, _ in records_dict:
    #         room_name_set.add(room_name)
    #     room_name_list = list(room_name_set)
    #     room_objects = Installation.objects.filter(group_id__in=int(room_name_list))
    #     room_dict = {room.room_name: room.room_id for room_objects}

    # TODO optimize and change for real room names (ids currently)
    @classmethod
    def save_records(cls, records_dict):
        for room_id, answers_list in records_dict.items():
            try:
                room = Installation.objects.get(id=int(room_id))
            except models.ObjectDoesNotExist:
                continue

            answer_object_list = []
            for answer in answers_list:
                answer_object_list.append(Answer(
                    installation=room,
                    keyword=answer['keyword'],
                    text=answer['text']
                ))
            cls.objects.bulk_create(answer_object_list)

    def __str__(self):
        return self.keyword