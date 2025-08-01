from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path("", views.home_view, name="home"),
    path('feed/', views.feed_view, name='feed'),
    path("create/", views.create_post, name='create'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:pk>/like-ajax/', views.like_post_ajax, name='like-ajax'),
]