from django.urls import path
from .views import follow_toggle, followers_list, following_list

app_name = 'follow'

urlpatterns = [
    path('toggle/<str:username>/', follow_toggle, name='toggle'),
    path('followers/<str:username>/', followers_list, name='followers'),
    path('following/<str:username>/', following_list, name='following'),
]
