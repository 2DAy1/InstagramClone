import random
import uuid

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

import requests
from faker import Faker
import cloudinary.uploader

from posts.models import Post, PostImage, Tag, PostTag, Comment, Like
from user.models import Profile

fake = Faker()


class Command(BaseCommand):
    help = "Seed DB with users, avatars, posts+images, tags, comments, likes (images from Picsum)"

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=2, help="Number of users")
        parser.add_argument('--posts', type=int, default=3, help="Posts per user")
        parser.add_argument('--comments', type=int, default=2, help="Comments per post")
        parser.add_argument('--likes', type=int, default=2, help="Likes per post")

    def _fetch_image(self, width=400, height=300):
        seed = uuid.uuid4().hex
        url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        resp = requests.get(url)
        resp.raise_for_status()
        name = f"{seed}.jpg"
        return ContentFile(resp.content, name=name)

    def handle(self, *args, **options):
        User = get_user_model()
        seed_group, _ = Group.objects.get_or_create(name='seed')

        users = []
        # 1) Створюємо користувачів + аватари
        for _ in range(options['users']):
            u = User.objects.create_user(
                username=f"seed_{fake.user_name()}",
                email=fake.email(),
                full_name=fake.name(),
                password="password123",
            )
            u.groups.add(seed_group)

            profile, _ = Profile.objects.get_or_create(user=u)
            avatar_file = self._fetch_image(100, 100)

            # Завантажуємо в Cloudinary
            upload_res = cloudinary.uploader.upload(avatar_file)
            # Записуємо public_id
            profile.avatar = upload_res['public_id']
            profile.save()

            users.append(u)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(users)} seed users"))

        # 2) Генеруємо теги
        tag_names = list({fake.word() for _ in range(40)})[:20]
        tags = [Tag.objects.get_or_create(name=n)[0] for n in tag_names]

        # 3) Для кожного користувача — пости, картинки, теги, коментарі, лайки
        for user in users:
            for _ in range(options['posts']):
                with transaction.atomic():
                    post = Post.objects.create(
                        author=user,
                        caption=fake.sentence(nb_words=12),
                    )

                    # a) картинки
                    for _ in range(random.randint(1, 3)):
                        img_file = self._fetch_image()
                        res = cloudinary.uploader.upload(img_file)
                        PostImage.objects.create(post=post, image=res['public_id'])

                    # b) теги
                    for tag in random.sample(tags, k=random.randint(1, 5)):
                        PostTag.objects.get_or_create(post=post, tag=tag)

                    # c) коментарі
                    for _ in range(options['comments']):
                        commenter = random.choice(users)
                        Comment.objects.create(
                            post=post,
                            author=commenter,
                            content=fake.sentence(nb_words=8)
                        )

                    # d) лайки
                    for liker in random.sample(users, k=min(len(users), options['likes'])):
                        Like.objects.get_or_create(post=post, user=liker)

        self.stdout.write(self.style.SUCCESS("🎉 Seeding done!"))
