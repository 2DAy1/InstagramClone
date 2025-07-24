from django.urls import path
from . import views

app_name = 'accounts'
urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('signup/sent/', views.activation_sent_view, name='activation_sent'),
    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('require_email/', views.require_email_view, name='require_email'),

    path('login/', views.login_view, name='login'),

    path('logout/', views.logout_view, name='logout'),
]
