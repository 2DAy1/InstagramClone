from django.urls import path
from .views import follow_toggle_ajax, followers_list, following_list

app_name = 'follow'

urlpatterns = [
    path('toggle/<str:username>/', follow_toggle_ajax, name='toggle-ajax'),
    path('followers/<str:username>/', followers_list, name='followers'),
    path('following/<str:username>/', following_list, name='following'),
]
