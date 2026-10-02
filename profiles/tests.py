import datetime
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from profiles.models import Education, Experience, Profile, Skill, SocialLink

User = get_user_model()


class ProfilesTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='elvis', email='elvis@test.com', password='password123')
        self.client.login(username='elvis', password='password123')
        self.profile = self.user.profile

    def test_profile_auto_created_by_signal(self):
        self.assertIsNotNone(self.profile)
        self.assertEqual(self.profile.email_public, 'elvis@test.com')

    def test_score_calculation(self):
        # Empty profile
        score = self.profile.professional_score
        self.assertEqual(score, 0)
        self.assertIn("Ajoute tes compétences", self.profile.missing_items)

        # Fill identity
        self.profile.full_name = "Elvis Sebgo"
        self.profile.profession = "Développeur Fullstack"
        self.profile.bio = "Passionné d'IA et de Python."
        self.profile.save()
        self.assertEqual(self.profile.professional_score, 15)

        # Add skills
        Skill.objects.create(profile=self.profile, name="Django")
        self.assertEqual(self.profile.professional_score, 30)

        # Add experience
        Experience.objects.create(
            profile=self.profile,
            title="Dev Django",
            company="Tech Corp",
            start_date=datetime.date(2022, 1, 1),
            is_current=True
        )
        self.assertEqual(self.profile.professional_score, 45)

        # Add education
        Education.objects.create(
            profile=self.profile,
            degree="Master Informatique",
            school="Université",
            start_date=datetime.date(2020, 9, 1),
            end_date=datetime.date(2022, 6, 30)
        )
        self.assertEqual(self.profile.professional_score, 60)

    def test_dashboard_view(self):
        response = self.client.get(reverse('profiles:dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ton profil")
        self.assertContains(response, "Professional score")

    def test_edit_profile_view(self):
        response = self.client.post(reverse('profiles:edit_profile'), {
            'full_name': 'Elvis Sebgo',
            'profession': 'Lead Developer',
            'location': 'Paris',
            'bio': 'Nouvelle bio testée.',
            'email_public': 'contact@elvis.pro',
            'phone': '+33123456789',
            'availability': 'Disponible immédiatement',
            'primary_color': '#E8231A',
        })
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.full_name, 'Elvis Sebgo')
        self.assertEqual(self.profile.profession, 'Lead Developer')

    def test_skills_crud(self):
        # Create
        response = self.client.post(reverse('profiles:skills'), {
            'name': 'Python',
            'level': 4
        })
        self.assertEqual(response.status_code, 302)
        skill = self.profile.skills.get(name='Python')
        self.assertEqual(skill.level, 4)

        # Delete
        response = self.client.post(reverse('profiles:delete_skill', kwargs={'pk': skill.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.profile.skills.filter(name='Python').exists())
