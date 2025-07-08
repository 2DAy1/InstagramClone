from django.urls import path
from . import views

app_name = 'posts'
urlpatterns = [
    path("", views.home_view, name="home"),
    path("create/", views.create_post, name='create'),
    path('<int:pk>/', views.post_detail, name='post_detail'),
    path('<int:post_pk>/thumbnail/<int:image_pk>/', views.thumbnail_view, name='thumbnail'),
]