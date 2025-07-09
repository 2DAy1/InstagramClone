from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.conf import settings

from .forms import SignUpForm, LoginForm
from .decorators import user_not_authenticated
from .tokens import account_activation_token

User = get_user_model()


def activate(request, uidb64, token):
    try:
        uid  = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        user.backend = settings.AUTHENTICATION_BACKENDS[0]
        login(request, user)
        messages.success(request, "Thank you for confirming your email. You are now logged in.")
        return redirect('posts:home')
    messages.error(request, "Activation link is invalid or expired.")
    return redirect('accounts:signup')


def activate_email(request, user, to_email):
    domain = get_current_site(request).domain

    uid   = urlsafe_base64_encode(force_bytes(user.pk))
    token = account_activation_token.make_token(user)

    path = reverse('accounts:activate', kwargs={'uidb64': uid, 'token': token})
    activation_link = f"http://{domain}{path}"

    mail_subject = "Activate your account"
    message = render_to_string("accounts/activation_email.html", {
        'user': user.full_name,
        'activation_link': activation_link,
        'domain': domain,
    })

    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f'Dear {user.username}, check your email at {to_email} for the activation link.'
        )
    else:
        messages.error(
            request,
            f'Problem sending email to {to_email}. Please verify the address.'
        )


@user_not_authenticated(redirect_url_name='posts:home')
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            activate_email(request, user, user.email)
            return redirect('accounts:activation_sent')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


@user_not_authenticated(redirect_url_name='posts:home')
def activation_sent_view(request):
    return render(request, 'accounts/activation_sent.html')

@user_not_authenticated(redirect_url_name='posts:home')
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password   = form.cleaned_data['password']
            user = authenticate(request, username=identifier, password=password)
            if user:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('posts:home')
            form.add_error(None, "Invalid username/email/phone or password.")
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, "Logged out successfully!")
    return redirect('accounts:login')
