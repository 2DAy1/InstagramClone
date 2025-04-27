from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.conf import settings

from .forms import SignUpForm, LoginForm


def signup_view(request):
    """
    View that handles user registration using SignUpForms
    """
    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = settings.AUTHENTICATION_BACKENDS[0]
            login(request, user)
            messages.success(request, "Your account has been created successfully.")
            return redirect('posts:home')
    else:
        form = SignUpForm()

    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            identifier = form.cleaned_data['identifier']
            password = form.cleaned_data['password']
            user = authenticate(request, username=identifier, password=password)

            if user is not None:
                login(request, user)
                return redirect('posts:home')
            else:
                form.add_error(None, "Invalid credentials.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})
