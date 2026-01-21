# carsite/management/commands/clear_old_cars.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from carsite.models import Car

class Command(BaseCommand):
    help = 'Удаляет объявления старше 1 года'

    def handle(self, *args, **options):
        old_cars = Car.objects.filter(
            created_at__lt=timezone.now() - timedelta(days=365)
        )
        count = old_cars.delete()[0]
        self.stdout.write(f"Удалено {count} старых объявлений")