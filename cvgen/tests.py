import datetime
import io
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from PIL import Image

from cvgen.models import CVTheme
from cvgen.services import build_cv_pdf
from profiles.models import Education, Experience, Skill

User = get_user_model()


class CVGenTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='cvtester', password='password123')
        self.client.login(username='cvtester', password='password123')
        self.profile = self.user.profile
        self.profile.full_name = "Jane Doe"
        self.profile.profession = "Data Scientist"
        self.profile.bio = "Experte en Machine Learning."
        self.profile.email_public = "jane@example.com"
        self.profile.phone = "0102030405"
        self.profile.location = "Lyon"
        self.profile.save()

        Skill.objects.create(profile=self.profile, name="Python")
        Experience.objects.create(
            profile=self.profile,
            title="Data Scientist",
            company="AI Corp",
            start_date=datetime.date(2021, 1, 1),
            is_current=True,
            description="Création de modèles NLP"
        )
        Education.objects.create(
            profile=self.profile,
            degree="Ingénieur",
            school="Polytechnique",
            start_date=datetime.date(2018, 9, 1),
            end_date=datetime.date(2021, 6, 30)
        )

        # Create a sample theme
        img = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        img.save(img_bytes, format='JPEG')
        img_bytes.seek(0)
        uploaded = SimpleUploadedFile('test_theme.jpg', img_bytes.read(), content_type='image/jpeg')

        self.theme = CVTheme.objects.create(
            name="Modern Sidebar",
            reference_image=uploaded,
            design_spec={
                'palette': ['#007ACC', '#222222'],
                'typography_mood': 'modern',
                'layout_archetype': 'sidebar',
                'spacing': 'comfortable',
            }
        )

    def test_build_cv_pdf_single_column(self):
        # Default with no theme
        self.profile.cv_theme = None
        self.profile.save()
        pdf_buffer = build_cv_pdf(self.profile)
        self.assertGreater(len(pdf_buffer.getvalue()), 1000)
        self.assertTrue(pdf_buffer.getvalue().startswith(b'%PDF'))

    def test_build_cv_pdf_sidebar(self):
        self.profile.cv_theme = self.theme
        self.profile.save()
        pdf_buffer = build_cv_pdf(self.profile)
        self.assertGreater(len(pdf_buffer.getvalue()), 1000)
        self.assertTrue(pdf_buffer.getvalue().startswith(b'%PDF'))

    def test_build_cv_pdf_header_band(self):
        self.theme.design_spec['layout_archetype'] = 'header-band'
        self.theme.save()
        self.profile.cv_theme = self.theme
        self.profile.save()
        pdf_buffer = build_cv_pdf(self.profile)
        self.assertGreater(len(pdf_buffer.getvalue()), 1000)
        self.assertTrue(pdf_buffer.getvalue().startswith(b'%PDF'))

    def test_generate_cv_view(self):
        response = self.client.post(reverse('cvgen:generate'))
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertTrue(bool(self.profile.cv_pdf))
        self.assertTrue(self.profile.cv_pdf.storage.exists(self.profile.cv_pdf.name))

    def test_preview_cv_view(self):
        response = self.client.get(reverse('cvgen:preview'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('inline', response['Content-Disposition'])

    def test_download_cv_view(self):
        response = self.client.get(reverse('cvgen:download'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment', response['Content-Disposition'])

    def test_choose_and_select_theme(self):
        response = self.client.get(reverse('cvgen:choose_theme'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Modern Sidebar")

        # Select theme
        response = self.client.post(reverse('cvgen:select_theme', kwargs={'pk': self.theme.pk}))
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertEqual(self.profile.cv_theme, self.theme)

        # Clear theme
        response = self.client.post(reverse('cvgen:clear_theme'))
        self.assertEqual(response.status_code, 302)
        self.profile.refresh_from_db()
        self.assertIsNone(self.profile.cv_theme)
