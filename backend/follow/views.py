from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .models import Subscription

User = get_user_model()

@login_required
def followers_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    subs = Subscription.objects.filter(target=user_obj).select_related('subscriber')
    followers = [sub.subscriber for sub in subs]
    return render(request, 'follow/followers_list.html', {
        'profile_user': user_obj,
        'followers': followers,
    })

@login_required
def following_list(request, username):
    user_obj = get_object_or_404(User, username=username)
    subs = Subscription.objects.filter(subscriber=user_obj).select_related('target')
    following = [sub.target for sub in subs]
    return render(request, 'follow/following_list.html', {
        'profile_user': user_obj,
        'following': following,
    })

@login_required
@require_POST
def follow_toggle_ajax(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({'error': "You cannot subscribe to yourself."}, status=400)

    sub, created = Subscription.objects.get_or_create(subscriber=request.user, target=target)
    if not created:
        sub.delete()
        is_following = False
    else:
        is_following = True

    followers_count = Subscription.objects.filter(target=target).count()
    return JsonResponse({
        'is_following': is_following,
        'followers_count': followers_count,
    })
