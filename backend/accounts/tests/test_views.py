from django.test import TestCase, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.core import mail
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes

from backend.accounts.tokens import account_activation_token

User = get_user_model()

@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class AccountsViewsTests(TestCase):
    def setUp(self):
        self.signup_url      = reverse('accounts:signup')
        self.activation_sent = reverse('accounts:activation_sent')
        self.activate_name   = 'accounts:activate'
        self.login_url       = reverse('accounts:login')
        self.logout_url      = reverse('accounts:logout')
        self.home_url        = reverse('posts:home')

    def test_signup_sends_email_and_redirects(self):
        data = {
            'username':     'alice',
            'full_name':    'Alice',
            'email':        'alice@example.com',
            'phone_number': '',
            'password1':    'Secret123',
            'password2':    'Secret123',
        }
        resp = self.client.post(self.signup_url, data)
        self.assertRedirects(resp, self.activation_sent)
        # створився користувач, але він неактивний
        u = User.objects.get(username='alice')
        self.assertFalse(u.is_active)
        # один лист у сховище
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/accounts/activate/', mail.outbox[0].body)

    def test_activation_with_valid_token(self):
        u = User.objects.create_user(
            username='bob',
            full_name='Bob',
            email='bob@x.com',
            password='pw',
            is_active=False
        )
        uid   = urlsafe_base64_encode(force_bytes(u.pk))
        token = account_activation_token.make_token(u)

        url   = reverse(self.activate_name, kwargs={'uidb64': uid, 'token': token})
        resp  = self.client.get(url)
        self.assertRedirects(resp, self.home_url)
        u.refresh_from_db()
        self.assertTrue(u.is_active)

    def test_activation_with_invalid_token(self):
        u = User.objects.create_user(username='carol', full_name='Carol', email='carol@x.com', password='pw', is_active=False)
        uid = urlsafe_base64_encode(force_bytes(u.pk))
        url = reverse(self.activate_name, kwargs={'uidb64': uid, 'token': 'wrong'})
        resp = self.client.get(url)
        self.assertRedirects(resp, self.signup_url)
        u.refresh_from_db()
        self.assertFalse(u.is_active)

    def test_login_success(self):
        u = User.objects.create_user(username='dave', full_name='Dave', email='dave@x.com', password='pw', is_active=True)
        resp = self.client.post(self.login_url, {'identifier': 'dave', 'password': 'pw'})
        self.assertRedirects(resp, self.home_url)
        self.assertTrue(resp.wsgi_request.user.is_authenticated)

    def test_logout_redirects_home(self):
        u = User.objects.create_user(
            username='eve', full_name='Eve',
            email='eve@x.com', password='pw', is_active=True
        )
        self.client.login(username='eve', password='pw')
        resp = self.client.get(self.logout_url)
        self.assertRedirects(resp, self.login_url)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_activation_sent_page_renders(self):
        resp = self.client.get(self.activation_sent)
        self.assertEqual(resp.status_code, 200)
        self.assertContains(resp, 'Thank you')

