from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

User = get_user_model()

class Command(BaseCommand):
    help = "Видаляє всіх користувачів із групи 'seed' і всі їх дані (каскадно)."

    def handle(self, *args, **options):
        try:
            group = Group.objects.get(name='seed')
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING("Група 'seed' не знайдена."))
            return

        users = User.objects.filter(groups=group)
        count = users.count()
        if not count:
            self.stdout.write(self.style.WARNING("Немає користувачів у групі 'seed'."))
            return

        # Просто видаляємо — все інше піде каскадом!
        users.delete()
        self.stdout.write(self.style.SUCCESS(f"✅ Видалено {count} seed-користувач(ів) і всі зв’язані з ними дані!"))
