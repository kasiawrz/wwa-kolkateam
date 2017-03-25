from django.core.management.base import BaseCommand, CommandError
from answers.models import Answer


class Command(BaseCommand):
    help = 'Fetches answers data from repository'

    def handle(self, *args, **options):
        Answer.fetch_data()