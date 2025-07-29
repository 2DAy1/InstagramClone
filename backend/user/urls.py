from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('edit/', views.edit_profile_view, name='edit_profile'),
    path('<str:username>/', views.profile_view, name='profile'),
]
