from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import PostForm
from .services import CreatePostService
from .models import Post

@login_required
def home_view(request):
    posts = Post.objects.all().order_by("-created_at")
    return render(request, 'posts/home.html', {'posts':posts})


@login_required
def create_post(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            CreatePostService(request.user, form).create()
            return redirect("posts:home")
    else:
        form = PostForm()
    return render(request, 'posts/create_post.html', {"form":form})

