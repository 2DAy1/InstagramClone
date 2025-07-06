from django.db import models
from django.conf import settings

def user_directory_path(instance, filename):
    """
    Function for saving avatars in the user_<id> directory.
    """
    return f'user_{instance.user.id}/{filename}'


class Profile(models.Model):
    """
    Model user profile.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateTimeField(null=True, blank=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"



