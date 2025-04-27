from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class AccountsViewsTests(TestCase):

    def setUp(self):
        self.signup_url = reverse('accounts:signup')
        self.login_url = reverse('accounts:login')
        self.logout_url = reverse('accounts:logout')
        self.home_url = reverse('posts:home')

        # Створимо тестового користувача
        self.user = User.objects.create_user(
            username="testuser",
            full_name="Test User",
            password="testpassword123",
            email="testuser@example.com"
        )

    def test_signup_view_success(self):
        """
        Перевіряємо успішну реєстрацію користувача
        """
        response = self.client.post(self.signup_url, {
            'username': 'newuser',
            'full_name': 'New User',
            'contact': 'newuser@example.com',
            'password1': 'newpassword123',
            'password2': 'newpassword123',
        })

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, self.home_url)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_login_view_success(self):
        """
        Перевіряємо успішний логін користувача
        """
        response = self.client.post(self.login_url, {
            'identifier': 'testuser',  # бо можна по username, email або phone
            'password': 'testpassword123',
        })

        self.assertEqual(response.status_code, 302)  # Redirect
        self.assertRedirects(response, self.home_url)
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_logout_view_success(self):
        """
        Перевіряємо успішний логаут користувача
        """
        self.client.login(username='testuser', password='testpassword123')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)

    def test_home_view_requires_login(self):
        """
        Перевіряємо що сторінка home захищена і перекидає на логін якщо не залогінен
        """
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, 302)
        login_url = f"{self.login_url}?next={self.home_url}"
        self.assertRedirects(response, login_url)
