from django.test import TestCase
from accounts.forms import SignUpForm
from accounts.models import User


class SignUpFromTests(TestCase):
    def test_valid_form_with_email(self):
        form = SignUpForm(data={
            'username': 'testuser',
            'full_name': 'Test User',
            'contact': 'test@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertTrue(form.is_valid())

    def test_valid_form_with_phone(self):
        form = SignUpForm(data={
            'username': 'testuser2',
            'full_name': 'User Two',
            'contact': '+380991234567',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertTrue(form.is_valid())

    def test_invalid_when_contact_empty(self):
        form = SignUpForm(data={
            'username': 'testuser3',
            'full_name': 'Empty Contact',
            'contact': '',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contact', form.errors)

    def test_invalid_when_passwords_dont_match(self):
        form = SignUpForm(data={
            'username': 'testuser4',
            'full_name': 'Mismatch',
            'contact': 'email@example.com',
            'password1': 'Pass123',
            'password2': 'OtherPass456',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)

    def test_duplicate_email(self):
        User.objects.create_user(username='existing', full_name='Exists', email='dupe@example.com', password='test123')
        form = SignUpForm(data={
            'username': 'newuser',
            'full_name': 'New User',
            'contact': 'dupe@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contact', form.errors)

    def test_duplicate_phone(self):
        User.objects.create_user(username='existing', full_name='Exists', phone_number='+380991234567',
                                 password='test123')
        form = SignUpForm(data={
            'username': 'newuser',
            'full_name': 'New User',
            'contact': '+380991234567',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contact', form.errors)

    def test_duplicate_username(self):
        User.objects.create_user(username='takenname', full_name='Taken', email='someone@example.com',
                                 password='test123')
        form = SignUpForm(data={
            'username': 'takenname',
            'full_name': 'New User',
            'contact': 'new@example.com',
            'password1': 'StrongPass123',
            'password2': 'StrongPass123',
        })
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
