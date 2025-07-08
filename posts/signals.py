import os
import shutil

from django.db.models.signals import post_delete
from django.dispatch import receiver
from django.conf import settings

from .models import Post, PostImage

@receiver(post_delete, sender=PostImage)
def delete_image_file(sender, instance, **kwargs):
    if instance.image:
        instance.image.delete(save=False)

@receiver(post_delete, sender=Post)
def delete_post_folder(sender, instance, **kwargs):
    post_dir = os.path.join(
        settings.MEDIA_ROOT,
        'posts',
        f'user_{instance.author.id}',
        f'post_{instance.id}'
    )
    if os.path.isdir(post_dir):
        shutil.rmtree(post_dir)
