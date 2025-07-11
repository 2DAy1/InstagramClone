from posts.models import Post, PostImage, Tag, PostTag
from typing import Optional
from django.db import transaction

class CreatePostService:
    def __init__(self, user, form):
        self.user = user
        self.form = form
        self.post: Optional[Post] = None

    def create(self):
        with transaction.atomic():
            self._create_post()
            self._save_images()
            self._assign_tags()
        return self.post

    def _create_post(self):
        self.post = self.form.save(commit=False)
        self.post.author = self.user
        self.post.save()

    def _save_images(self):
        images = self.form.files.getlist("images")
        for img in images:
            PostImage.objects.create(post=self.post, image=img)

    def _assign_tags(self):
        raw = self.form.cleaned_data['tags']
        names = {t.strip().lower() for t in raw.split(',') if t.strip()}
        PostTag.objects.filter(post=self.post).exclude(tag__name__in=names).delete()
        for name in names:
            tag, _ = Tag.objects.get_or_create(name=name)
            PostTag.objects.get_or_create(post=self.post, tag=tag)
