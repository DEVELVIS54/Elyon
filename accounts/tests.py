from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTests(TestCase):
    def test_user_registration(self):
        response = self.client.post(reverse('accounts:register'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'P@ssword123!',
            'password2': 'P@ssword123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profiles:onboarding'))
        
        user = User.objects.get(username='newuser')
        self.assertIsNotNone(user)
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.email_public, 'newuser@example.com')

    def test_register_already_authenticated_redirects(self):
        user = User.objects.create_user(username='authuser', password='password123')
        self.client.login(username='authuser', password='password123')
        response = self.client.get(reverse('accounts:register'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profiles:dashboard'))

    def test_login_and_logout(self):
        User.objects.create_user(username='testuser', password='password123')
        response = self.client.post(reverse('accounts:login'), {
            'username': 'testuser',
            'password': 'password123',
        })
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('profiles:dashboard'))

        # Logout
        response = self.client.post(reverse('accounts:logout'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('home'))
