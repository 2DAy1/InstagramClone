from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch
from .forms import PostForm, CommentForm
from .services import CreatePostService
from .models import Post, Comment

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

@login_required
def post_detail(request, pk):
    qs = (
        Post.objects
            .select_related('author')
            .prefetch_related(
                'images',
                Prefetch(
                    'comments',
                    queryset=Comment.objects.select_related('author')
                )
            )
    )
    post = get_object_or_404(qs, pk=pk)

    # Закинути в окрему функцію create_comment
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect('post:post_detail', pk=post.pk)
    else:
        form = CommentForm()

    return render(request, 'post/detail.html', {
        'post': post,
        'comment_form': form,
    })


from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from .models import PostImage
from PIL import Image as PilImage
from io import BytesIO

def thumbnail_view(request, post_pk, image_pk):
    img_obj = get_object_or_404(PostImage, pk=image_pk, post_id=post_pk)
    img = PilImage.open(img_obj.image.path)
    img = img.convert('RGB')
    img.thumbnail((300, 300), PilImage.Resampling.LANCZOS)

    buf = BytesIO()
    img.save(
        buf,
        format='JPEG',
        quality=90,
        optimize=True,
        progressive=True
    )

    return HttpResponse(buf.getvalue(), content_type='image/jpeg')