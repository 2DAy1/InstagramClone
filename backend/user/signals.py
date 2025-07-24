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



def get_cloudinary_public_id(field):
    """
    Коректно отримує Cloudinary public_id з CloudinaryField або повертає None.
    """
    if hasattr(field, 'public_id'):
        pid = field.public_id
    else:
        val = str(field) if field is not None else None
        pid = val if isinstance(val, str) and val and val != 'None' else None
    return pid

@receiver(post_delete, sender=Profile)
def delete_avatar_in_cloudinary(sender, instance, **kwargs):
    avatar_field = getattr(instance, 'avatar', None)
    pid = get_cloudinary_public_id(avatar_field)
    if pid:
        try:
            destroy(pid, resource_type='image', invalidate=True)
        except Exception:
            pass