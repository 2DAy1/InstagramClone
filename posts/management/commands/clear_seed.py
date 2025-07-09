from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Delete all seed users (group 'seed') and cascade‐delete їх контент"

    def handle(self, *args, **options):
        try:
            seed_group = Group.objects.get(name='seed')
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING("Group 'seed' не знайдено — нічого видаляти."))
            return

        seed_users = seed_group.user_set.all()
        count = seed_users.count()
        if count == 0:
            self.stdout.write(self.style.WARNING("У групі 'seed' немає користувачів."))
            return

        with transaction.atomic():
            seed_users.delete()
            seed_group.delete()

        self.stdout.write(self.style.SUCCESS(
            f"🗑️ Видалено {count} seed‐користувачів та їх дані."
        ))
