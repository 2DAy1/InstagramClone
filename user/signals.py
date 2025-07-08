import os
import shutil

from django.db.models.signals import post_save, post_delete
from django.conf import settings

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import Profile



@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_media(sender, instance, **kwargs):
    avatar_dir = os.path.join(settings.MEDIA_ROOT, 'users', 'avatars', f'user_{instance.id}')
    posts_dir  = os.path.join(settings.MEDIA_ROOT, 'users','posts', f'user_{instance.id}')

    for path in (avatar_dir, posts_dir):
        if os.path.isdir(path):
            shutil.rmtree(path, ignore_errors=True)



@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)