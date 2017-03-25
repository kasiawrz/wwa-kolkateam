from django.db import models

from core.models import Installation
from answers.utils import get_repo_from_git


class Answer(models.Model):
    keyword = models.CharField(max_length=30)
    text = models.TextField()
    installation = models.ForeignKey('core.Installation', related_name='answers')
    likes_count = models.PositiveIntegerField(default=0)
    dislikes_count = models.PositiveIntegerField(default=0)
    ask_count = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = ('installation', 'keyword')

    def increment_ask_counter(self):
        self.ask_count += 1
        self.save()

    def like(self):
        self.likes_count += 1
        self.save()

    def dislike(self):
        self.dislikes_count += 1
        self.save()

    @classmethod
    def save_records(cls, records_dict):
        for room_id, answers_list in records_dict.items():
            try:
                room = Installation.objects.get(room_id=int(room_id))
            except models.ObjectDoesNotExist:
                continue

            answer_object_list = []
            file_room_keywords = {answer['keyword'] for answer in answers_list}
            database_room_keywords = {answer.keyword for answer in room.answers.all()}
            keywords_to_create = file_room_keywords - database_room_keywords
            keywords_to_delete = database_room_keywords - file_room_keywords

            for answer in answers_list:
                if answer['keyword'] not in keywords_to_create:
                    continue
                answer_object_list.append(Answer(
                    installation=room,
                    keyword=answer['keyword'],
                    text=answer['text']
                ))
            cls.objects.bulk_create(answer_object_list)
            room.answers.filter(keyword__in=list(keywords_to_delete)).delete()

    @classmethod
    def fetch_data(cls):
        records = get_repo_from_git()
        cls.save_records(records)

    def __str__(self):
        return self.keyword