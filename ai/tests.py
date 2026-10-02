from unittest.mock import patch
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from django.urls import reverse

from ai.services import AIServiceError, _sanitize_design_spec, call_groq

User = get_user_model()


class AITests(TestCase):
    def test_sanitize_design_spec(self):
        raw = {
            'palette': ['#FF0000', '#00FF00', 'not-a-color'],
            'typography_mood': 'technical',
            'layout_archetype': 'sidebar',
            'spacing': 'spacious',
        }
        spec = _sanitize_design_spec(raw)
        self.assertEqual(spec['palette'], ['#FF0000', '#00FF00'])
        self.assertEqual(spec['typography_mood'], 'technical')
        self.assertEqual(spec['layout_archetype'], 'sidebar')
        self.assertEqual(spec['spacing'], 'spacious')

    def test_sanitize_design_spec_fallbacks(self):
        raw = {
            'palette': ['invalid'],
            'typography_mood': 'unknown',
            'layout_archetype': 'unknown',
            'spacing': 'unknown',
        }
        spec = _sanitize_design_spec(raw)
        self.assertEqual(spec['palette'], ['#E8231A', '#141414'])
        self.assertEqual(spec['typography_mood'], 'modern')
        self.assertEqual(spec['layout_archetype'], 'single-column')
        self.assertEqual(spec['spacing'], 'comfortable')

    @override_settings(GROQ_API_KEY='')
    def test_call_groq_without_api_key_raises_error(self):
        with self.assertRaises(AIServiceError):
            call_groq("Hello")

    @override_settings(GROQ_API_KEY='')
    def test_assistant_view_handles_missing_key(self):
        user = User.objects.create_user(username='aiuser', password='password123')
        self.client.login(username='aiuser', password='password123')
        response = self.client.post(
            reverse('ai:assistant'),
            data={'question': 'Aide-moi'},
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        data = response.json()
        self.assertFalse(data['ok'])
        self.assertIn('GROQ_API_KEY', data['error'])
