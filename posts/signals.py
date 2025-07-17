from django.db.models.signals import post_delete
from django.dispatch import receiver
from cloudinary.uploader import destroy

from .models import PostImage




@receiver(post_delete, sender=PostImage)
def delete_image_in_cloudinary(sender, instance, **kwargs):
    """
    Після видалення об'єкта PostImage в БД — видаляємо відповідний ресурс у Cloudinary.
    """
    # отримуємо public_id (рядок) з CloudinaryField
    pid = getattr(instance.image, 'public_id', None) or str(instance.image)
    if pid:
        try:
            destroy(pid, resource_type='image', invalidate=True)
        except Exception:
            pass
