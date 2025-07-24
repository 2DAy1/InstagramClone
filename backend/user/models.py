from django.db import models
from django.conf import settings
from django.templatetags.static import static
from cloudinary.models import CloudinaryField



class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = CloudinaryField('avatar')
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'public_id'):
            return self.avatar.build_url(width=150, height=150, crop='thumb', gravity='face')
        return static('img/default_avatar.jpg')


    def __str__(self):
        return f"{self.user.username}'s Profile"



