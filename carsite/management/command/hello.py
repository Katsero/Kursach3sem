# carsite/management/commands/hello.py
from django.core.management.base import BaseCommand
from carsite.models import User

class Command(BaseCommand):
    help = 'Выводит приветствие и количество пользователей'

    def handle(self, *args, **options):
        user_count = User.objects.count()
        self.stdout.write(
            self.style.SUCCESS(f'Привет! В системе {user_count} пользователей.')
        )