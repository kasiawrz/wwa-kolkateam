from django.db import models


class Answer(models.Model):
    keyword = models.CharField(max_length=30, db_index=True)
    text = models.TextField()
    installation = models.ForeignKey('core.Installation')

    def __str__(self):
        return self.keyword