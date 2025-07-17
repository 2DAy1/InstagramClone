from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

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
def follow_toggle(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        messages.error(request, "You cannot subscribe to yourself.")
        return redirect(reverse('user:profile', kwargs={'username': username}))

    sub, created = Subscription.objects.get_or_create(
        subscriber=request.user,
        target=target
    )
    if not created:
        sub.delete()
        messages.success(request, f"You have unsubscribed from {username}.")
    else:
        messages.success(request, f"You are now subscribed to {username}.")

    return redirect(reverse('user:profile', kwargs={'username': username}))
