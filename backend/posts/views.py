from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef, Prefetch, Subquery

from django.http import JsonResponse
from django.views.decorators.http import require_POST

from .forms import PostForm, CommentForm
from .services import CreatePostService
from .models import Post, Comment, Like, PostImage



User = get_user_model()



@login_required
def home_view(request):
    liked_subq = Like.objects.filter(post=OuterRef('pk'), user=request.user)
    first_image = PostImage.objects.filter(post=OuterRef('pk')).order_by('id')
    posts = (
        Post.objects
            .annotate(is_liked=Exists(liked_subq))
            .annotate(preview_image_url=Subquery(first_image.values('image')[:1]))
            .order_by('-created_at')
    )
    return render(request, 'posts/home.html', {'posts': posts})


@login_required
def feed_view(request):
    following = request.user.following_set.values_list('target_id', flat=True)
    first_image = PostImage.objects.filter(post=OuterRef('pk')).order_by('id')
    qs = (
        Post.objects
            .filter(author_id__in=following)
            .annotate(preview_image_url=Subquery(first_image.values('image')[:1]))
            .select_related('author')
            .order_by('-created_at')
    )
    return render(request, 'posts/feed.html', {'posts':qs})


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




@login_required
def post_detail(request, pk):
    liked_subq = Like.objects.filter(post=OuterRef('pk'), user=request.user)
    post_qs = Post.objects.annotate(is_liked=Exists(liked_subq))
    post = get_object_or_404(post_qs, pk=pk)

    # Закинути в окрему функцію create_comment
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('posts:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'posts/detail.html', {
        'post': post,
        'comment_form': form,
    })






@login_required
@require_POST
def like_post_ajax(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like_qs = Like.objects.filter(post=post, user=request.user)
    if like_qs.exists():
        like_qs.delete()
        liked = False
    else:
        Like.objects.create(post=post, user=request.user)
        liked = True
    return JsonResponse({
        'liked': liked,
        'likes_count': post.likes.count(),
    })