from posts.models import Post, PostImage, Tag, PostTag
from typing import Optional

class CreatePostService:
    def __init__(self, user, form):
        self.user = user
        self.form = form
        self.post: Optional[Post] = None

    def create(self):
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
        for image in images:
            PostImage.objects.create(post=self.post, image=image)

    def _assign_tags(self):
        raw_tags = self.form.cleaned_data.get('tags')
        tag_names = [tag.strip().lower() for tag in raw_tags.split(',') if tag.strip()]
        for name in tag_names:
            tag, _ = Tag.objects.get_or_create(name=name)
            PostTag.objects.get_or_create(post=self.post, tag=tag)
