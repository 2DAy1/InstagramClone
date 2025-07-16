import random
import uuid

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction

import requests
from faker import Faker

from posts.models import Post, PostImage, Tag, PostTag, Comment, Like
from user.models import Profile

fake = Faker()

class Command(BaseCommand):
    help = "Seed DB with users, avatars, posts+images, tags, comments, likes (images from Picsum)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--users', type=int, default=2,
            help="Number of users (default: 2)"
        )
        parser.add_argument(
            '--posts', type=int, default=3,
            help="Posts per user (default: 3)"
        )
        parser.add_argument(
            '--comments', type=int, default=2,
            help="Comments per post (default: 2)"
        )
        parser.add_argument(
            '--likes', type=int, default=2,
            help="Likes per post (default: 2)"
        )

    def _fetch_image(self, width=400, height=300):
        """
        Download random image from Picsum.photos as ContentFile (suitable for CloudinaryField).
        """
        seed = uuid.uuid4().hex
        url = f"https://picsum.photos/seed/{seed}/{width}/{height}"
        resp = requests.get(url)
        resp.raise_for_status()
        name = f"{seed}.jpg"
        return ContentFile(resp.content, name=name)

    def handle(self, *args, **options):
        num_users = options['users']
        num_posts = options['posts']
        num_comments = options['comments']
        num_likes = options['likes']

        User = get_user_model()
        seed_group, _ = Group.objects.get_or_create(name='seed')

        users = []
        # --- Create users and avatars ---
        for _ in range(num_users):
            username = f"seed_{fake.user_name()}"
            email = fake.email()
            full_name = fake.name()
            user = User.objects.create_user(
                username=username,
                email=email,
                full_name=full_name,
                password="password123",
            )
            user.groups.add(seed_group)
            # Create Profile + avatar (CloudinaryField)
            profile, _ = Profile.objects.get_or_create(user=user)
            avatar_file = self._fetch_image(100, 100)
            profile.avatar.save(avatar_file.name, avatar_file)
            profile.save()
            users.append(user)
        self.stdout.write(self.style.SUCCESS(f"✅ Created {len(users)} seed users"))

        # --- Create tags ---
        tag_names = list({fake.word() for _ in range(40)})[:20]
        tags = [Tag.objects.get_or_create(name=n)[0] for n in tag_names]

        # --- Create posts, images, tags, comments, likes ---
        for user in users:
            for _ in range(num_posts):
                with transaction.atomic():
                    post = Post.objects.create(
                        author=user,
                        caption=fake.sentence(nb_words=12),
                    )

                    # --- Images for post (1–3 random), через .image.save() ---
                    for _ in range(random.randint(1, 3)):
                        img_file = self._fetch_image()
                        post_image = PostImage(post=post)
                        post_image.image.save(img_file.name, img_file, save=True)

                    # --- Assign random tags to post ---
                    for t in random.sample(tags, k=random.randint(1, 5)):
                        PostTag.objects.get_or_create(post=post, tag=t)

                    # --- Comments (from random users) ---
                    for _ in range(num_comments):
                        commenter = random.choice(users)
                        Comment.objects.create(
                            post=post,
                            author=commenter,
                            content=fake.sentence(nb_words=8)
                        )

                    # --- Likes (random users) ---
                    like_users = random.sample(users, k=min(len(users), num_likes))
                    for liker in like_users:
                        Like.objects.get_or_create(post=post, user=liker)

        self.stdout.write(self.style.SUCCESS("🎉 Seeding done!"))
