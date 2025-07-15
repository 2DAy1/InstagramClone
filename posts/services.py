# posts/services.py
from typing import List, Optional
from django.db import transaction

from .models import Post, PostImage, Tag, PostTag

class CreatePostService:
    def __init__(
        self,
        user,
        caption: str,
        tags_raw: str,
        images: List,   # список InMemoryUploadedFile
    ):
        self.user = user
        self.caption = caption
        self.tags_raw = tags_raw
        self.images = images
        self.post: Optional[Post] = None

    def create(self):
        with transaction.atomic():
            self._create_post()
            self._save_images()
            self._assign_tags()
        return self.post

    def _create_post(self):
        self.post = Post.objects.create(
            author=self.user,
            caption=self.caption
        )

    def _save_images(self):
        for f in self.images:
            # f тут гарантовано UploadedFile, не рядок
            pi = PostImage(post=self.post)
            pi.image.save(f.name, f)
            # CloudinaryField/Storage сам зробить pi.save()

    def _assign_tags(self):
        names = {t.strip().lower() for t in self.tags_raw.split(",") if t.strip()}
        PostTag.objects.filter(post=self.post).exclude(tag__name__in=names).delete()
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            PostTag.objects.get_or_create(post=self.post, tag=tag)
