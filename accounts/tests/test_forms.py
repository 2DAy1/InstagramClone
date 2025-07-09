from django.test import TestCase
from django.contrib.auth import get_user_model
from accounts.forms import SignUpForm

User = get_user_model()


class SignUpFormTests(TestCase):
    def test_valid_with_email(self):
        form = SignUpForm(data={
            'username':     'alice',
            'full_name':    'Alice',
            'email':        'alice@example.com',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertTrue(form.is_valid())

    def test_valid_with_phone(self):
        form = SignUpForm(data={
            'username':     'bob',
            'full_name':    'Bob',
            'email':        'bob@example.com',
            'phone_number': '+380991234567',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertTrue(form.is_valid())

    def test_empty_email_and_phone(self):
        form = SignUpForm(data={
            'username':     'charlie',
            'full_name':    'Charlie',
            'email':        '',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_password_mismatch(self):
        form = SignUpForm(data={
            'username':     'dana',
            'full_name':    'Dana',
            'email':        'dana@example.com',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Other123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user(username='eve', full_name='Eve', email='eve@x.com', password='pass')
        form = SignUpForm(data={
            'username':     'eve',
            'full_name':    'New Eve',
            'email':        'new@x.com',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(username='frank', full_name='Frank', email='frank@x.com', password='pass')
        form = SignUpForm(data={
            'username':     'frank2',
            'full_name':    'Frank2',
            'email':        'frank@x.com',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

    def test_duplicate_phone(self):
        User.objects.create_user(username='gina', full_name='Gina', email='gina@x.com', phone_number='+380991112223', password='pass')
        form = SignUpForm(data={
            'username':     'gina2',
            'full_name':    'Gina2',
            'email':        'gina2@x.com',
            'phone_number': '+380991112223',
            'password1':    'Secret123',
            'password2':    'Secret123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('phone_number', form.errors)
