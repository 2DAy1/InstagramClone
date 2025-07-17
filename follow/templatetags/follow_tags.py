from django import template
from django.urls import reverse
from django.contrib.auth import get_user_model

register = template.Library()
User = get_user_model()

@register.inclusion_tag('follow/follow_button.html', takes_context=True)
def follow_button(context, profile_user):
    request_user = context['request'].user

    if not request_user.is_authenticated or request_user == profile_user:
        return {}

    is_following = request_user.following_set.filter(
        target=profile_user
    ).exists()
    toggle_url = reverse('follow:toggle', kwargs={'username': profile_user.username})

    return {
        'is_following': is_following,
        'toggle_url':   toggle_url,
    }
