# user/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings

from cloudinary.uploader import destroy

from .models import Profile

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Створює Profile автоматично при створенні User.
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_delete, sender=Profile)
def delete_avatar_in_cloudinary(sender, instance, **kwargs):
    """
    Після видалення Profile в БД — видаляємо avatar у Cloudinary.
    """
    avatar_field = instance.avatar
    pid = getattr(avatar_field, 'public_id', None) or str(avatar_field)
    if pid:
        try:
            destroy(pid, resource_type='image', invalidate=True)
        except Exception:
            pass
