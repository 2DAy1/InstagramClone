import random
import uuid
from django.core.management.base import BaseCommand
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from backend.posts.forms import PostForm, CommentForm
from backend.posts.models import PostImage, Tag, PostTag, Like
from backend.user.models import Profile
import requests

User = get_user_model()

# =================== Функції ===================

def fetch_image(width=400, height=300):
    """Отримати картинку з picsum.photos як SimpleUploadedFile"""
    seed = uuid.uuid4().hex
    url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
    resp = requests.get(url)
    resp.raise_for_status()
    name = f"{seed}.jpg"
    return SimpleUploadedFile(
        name=name,
        content=resp.content,
        content_type=resp.headers.get('Content-Type', 'image/jpeg')
    )

def create_user(i, group):
    """Створює одного користувача, повертає User"""
    user, created = User.objects.get_or_create(
        username=f"testuser{i+1}",
        defaults={
            "email": f"testuser{i+1}@mail.com",
            "phone_number": f"+3800000000{i+1}",
            "full_name": f"Test User {i+1}",
        }
    )
    user.groups.add(group)
    Profile.objects.get_or_create(user=user)
    return user

def create_post(user, j):
    """Створює пост через форму, повертає Post, tags_str і images"""
    caption = f"Test post {j+1} by {user.username}"
    tags_str = ', '.join([f"tag{random.randint(1,3)}" for _ in range(random.randint(1, 3))])
    n_images = random.randint(1, 3)
    images = [fetch_image() for _ in range(n_images)]

    post_form = PostForm(
        data={'caption': caption, 'tags': tags_str},
        files={'images': images}
    )
    if post_form.is_valid():
        post = post_form.save(commit=False)
        post.author = user
        post.save()
        post_form.save_m2m()
        return post, tags_str, images, None
    else:
        return None, tags_str, images, post_form.errors

def attach_images_to_post(post, images):
    """Привʼязати картинки до поста"""
    for img in images:
        PostImage.objects.create(post=post, image=img)

def attach_tags_to_post(post, tags_str):
    """Додає теги до поста"""
    if tags_str:
        for tag_str in [t.strip() for t in tags_str.split(',') if t.strip()]:
            tag_obj, _ = Tag.objects.get_or_create(name=tag_str)
            PostTag.objects.get_or_create(post=post, tag=tag_obj)

def create_comment(post, commenter):
    """Створити коментар через форму"""
    comment_form = CommentForm(data={
        'content': f"Test comment by {commenter.username} on post {post.id}"
    })
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.post = post
        comment.author = commenter
        comment.save()
        return comment, None
    else:
        return None, comment_form.errors

def create_like(post, liker):
    """Створити лайк"""
    Like.objects.get_or_create(post=post, user=liker)

# =================== Management Command ===================

class Command(BaseCommand):
    help = "Seed test users, posts, likes, comments with images via forms"

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=2)
        parser.add_argument('--posts', type=int, default=3)
        parser.add_argument('--comments', type=int, default=2)
        parser.add_argument('--likes', type=int, default=2)

    def handle(self, *args, **options):
        users_count = options['users']
        posts_per_user = options['posts']
        comments_per_post = options['comments']
        likes_per_post = options['likes']

        # 1. Users
        group, _ = Group.objects.get_or_create(name='seed')
        users = [create_user(i, group) for i in range(users_count)]

        # 2. Posts, Images, Tags
        posts = []
        for user in users:
            for j in range(posts_per_user):
                post, tags_str, images, errors = create_post(user, j)
                if post:
                    attach_images_to_post(post, images)
                    attach_tags_to_post(post, tags_str)
                    posts.append(post)
                    self.stdout.write(self.style.SUCCESS(
                        f"Created post {post.id} for {user.username} ({len(images)} images, tags: {tags_str})"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(f"Помилка у формі Post: {errors}"))

        # 3. Comments
        for post in posts:
            possible_commenters = [u for u in users if u != post.author]
            for _ in range(comments_per_post):
                commenter = random.choice(possible_commenters)
                comment, errors = create_comment(post, commenter)
                if comment:
                    self.stdout.write(self.style.SUCCESS(
                        f"Comment by {commenter.username} on post {post.id}"
                    ))
                else:
                    self.stdout.write(self.style.ERROR(f"Помилка у формі Comment: {errors}"))

        # 4. Likes
        for post in posts:
            possible_likers = [u for u in users if u != post.author]
            likers = random.sample(possible_likers, min(likes_per_post, len(possible_likers)))
            for liker in likers:
                create_like(post, liker)

        self.stdout.write(self.style.SUCCESS("✅ Seed data created!"))
