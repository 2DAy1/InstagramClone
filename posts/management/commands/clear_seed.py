# posts/management/commands/clear_seed.py

from django.core.management.base import BaseCommand
from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

import cloudinary.uploader
import cloudinary.api

from posts.models import PostImage
from user.models import Profile

class Command(BaseCommand):
    help = "Delete all seed users, their Cloudinary media, and cascade-delete all related content"

    def handle(self, *args, **options):
        User = get_user_model()

        # 1) Знаходимо групу та seed-користувачів
        try:
            seed_group = Group.objects.get(name='seed')
        except Group.DoesNotExist:
            self.stdout.write(self.style.WARNING("Group 'seed' not found — nothing to clear."))
            return

        seed_users = list(seed_group.user_set.all())
        if not seed_users:
            self.stdout.write(self.style.WARNING("No users in 'seed' group — nothing to clear."))
            return

        # 2) Збираємо public_id для PostImage
        image_ids = list(
            PostImage.objects
                     .filter(post__author__in=seed_users)
                     .values_list('image', flat=True)
        )
        # фільтруємо лише строки
        image_ids = [pid for pid in image_ids if isinstance(pid, str)]

        # 3) Збираємо public_id для avatar у Profile
        avatar_ids = []
        for u in seed_users:
            profile = getattr(u, 'profile', None)
            if profile and profile.avatar:
                pid = getattr(profile.avatar, 'public_id', None) or str(profile.avatar)
                if isinstance(pid, str):
                    avatar_ids.append(pid)

        # 4) Видаляємо всі PostImage за раз через Admin API
        if image_ids:
            cloudinary.api.delete_resources(
                image_ids,
                resource_type='image',
                type='upload',
                invalidate=True
            )
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(image_ids)} post images from Cloudinary."))

        # 5) Видаляємо аватари поштучно через Upload API destroy
        for pid in avatar_ids:
            cloudinary.uploader.destroy(pid, resource_type='image', invalidate=True)
        if avatar_ids:
            self.stdout.write(self.style.SUCCESS(f"Deleted {len(avatar_ids)} avatars from Cloudinary."))

        # 6) Каскадно видаляємо користувачів і групу в БД
        with transaction.atomic():
            for u in seed_users:
                u.delete()
            seed_group.delete()

        self.stdout.write(self.style.SUCCESS(
            f"🗑️ Cleared {len(seed_users)} seed users and all their related data."
        ))
