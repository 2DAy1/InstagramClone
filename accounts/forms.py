from django import forms
from django.core.exceptions import ValidationError
from .models import User
from .utils import is_valid_email, is_valid_phone_number

class SignUpForm(forms.Form):
    """
    User registration form.
    Accepts either an email or a phone number via the 'contact' field.
    """
    username = forms.CharField(max_length=150)
    full_name = forms.CharField(max_length=150)
    contact = forms.CharField(label='Email or phone number')
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError("This username is already taken")
        return username

    def clean_contact(self):
        contact = self.cleaned_data.get('contact')

        if is_valid_email(contact):
            if User.objects.filter(email__iexact=contact).exists():
                raise ValidationError("A user with this email already taken")
            self.cleaned_data['email']=contact
        elif is_valid_phone_number(contact):
            if User.objects.filter(phone_number=contact).exists():
                raise ValidationError('A user with this phone number already exists.')
            self.cleaned_data['phone_number'] = contact
        else:
            raise ValidationError("Enter a valid email address or phone number.")

        return contact

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        phone = cleaned_data.get('phone_number')
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if not email and not phone:
            raise forms.ValidationError("You must provide either an email or phone number.")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')


    def save(self):
        """
        Creates and returns a new user via the custom UserManager.
        Handles optional fields (email or phone_number).
        """
        username = self.cleaned_data["username"]
        full_name = self.cleaned_data["full_name"]
        password = self.cleaned_data["password1"]
        email = self.cleaned_data.get("email")
        phone = self.cleaned_data.get("phone_number")

        return User.objects.create_user(
            username=username,
            full_name=full_name,
            password=password,
            email=email,
            phone_number=phone
        )


class LoginForm(forms.Form):
    identifier = forms.CharField(label="Username / Email / Phone", max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)



