from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from .utils import is_valid_email, is_valid_phone_number

User = get_user_model()

class SignUpForm(forms.Form):
    username     = forms.CharField(max_length=150)
    full_name    = forms.CharField(max_length=150)
    email        = forms.EmailField(label='Email', max_length=254,
                                    help_text='A valid email address, please.')
    phone_number = forms.CharField(label='Phone (optional)', required=False, max_length=20)
    password1    = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2    = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data["username"]
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken")
        return username

    def clean_email(self):
        email = self.cleaned_data["email"]
        if not is_valid_email(email):
            raise ValidationError("Enter a valid email address.")
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("A user with this email already exists.")
        return email.lower()

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number') or ''
        if phone:
            if not is_valid_phone_number(phone):
                raise ValidationError("Enter a valid phone number.")
            if User.objects.filter(phone_number=phone).exists():
                raise ValidationError("A user with this phone number already exists.")
        return phone

    def clean(self):
        cd = super().clean()
        pwd1 = cd.get('password1')
        pwd2 = cd.get('password2')
        if pwd1 and pwd2 and pwd1 != pwd2:
            self.add_error('password2', 'Passwords do not match.')
        return cd

    def save(self):
        data = self.cleaned_data
        user = User.objects.create_user(
            username     = data['username'],
            full_name    = data['full_name'],
            email        = data['email'],
            phone_number = data.get('phone_number') or None,
            password     = data['password1'],
            is_active    = False,
        )
        return user

class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username / Email / Phone", max_length=150)
    password   = forms.CharField(label="Password", widget=forms.PasswordInput)
