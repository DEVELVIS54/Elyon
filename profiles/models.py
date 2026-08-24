from django.conf import settings
from django.db import models


PLAN_CHOICES = [
    ('free', 'Free'),
    ('pro', 'Pro'),
    ('business', 'Business'),
]


class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile'
    )

    # Identité
    photo = models.ImageField(upload_to='profiles/photos/', blank=True, null=True)
    full_name = models.CharField(max_length=150, blank=True)
    profession = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    email_public = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    availability = models.CharField(max_length=100, blank=True, help_text="Ex: Disponible pour missions freelance")

     # Couleur d'accent utilisée dans le CV généré (utilisée si aucun thème n'est choisi)
    primary_color = models.CharField(max_length=7, default='#E8231A')

    # Thème de CV choisi dans le catalogue (optionnel)
    cv_theme = models.ForeignKey(
        'cvgen.CVTheme', on_delete=models.SET_NULL, blank=True, null=True, related_name='profiles'
    )

    # Plan / SaaS
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES, default='free')

    # CV généré
    cv_pdf = models.FileField(upload_to='profiles/cv/', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username

    @property
    def professional_score(self):
        """Calcule un score sur 100 selon la complétude du profil (pertinent pour le CV)."""
        score = 0
        if self.full_name and self.profession and self.bio:
            score += 15
        if self.photo:
            score += 10
        if self.social_links.filter(platform='github').exists():
            score += 10
        if self.social_links.filter(platform='linkedin').exists():
            score += 10
        if self.skills.exists():
            score += 15
        if self.experiences.exists():
            score += 15
        if self.educations.exists():
            score += 15
        if self.cv_pdf:
            score += 10
        return min(score, 100)

    @property
    def missing_items(self):
        """Retourne une liste de conseils pour améliorer le score."""
        missing = []
        if not self.photo:
            missing.append("Ajoute une photo de profil")
        if not self.bio:
            missing.append("Rédige ta bio (ou laisse l'IA la générer)")
        if not self.social_links.filter(platform='github').exists():
            missing.append("Ajoute ton lien GitHub")
        if not self.social_links.filter(platform='linkedin').exists():
            missing.append("Ajoute ton lien LinkedIn")
        if not self.skills.exists():
            missing.append("Ajoute tes compétences")
        if not self.experiences.exists():
            missing.append("Ajoute une expérience professionnelle")
        if not self.educations.exists():
            missing.append("Ajoute une formation")
        if not self.cv_pdf:
            missing.append("Génère ton CV")
        return missing


SOCIAL_PLATFORM_CHOICES = [
    ('github', 'GitHub'),
    ('linkedin', 'LinkedIn'),
    ('facebook', 'Facebook'),
    ('instagram', 'Instagram'),
    ('x', 'X (Twitter)'),
    ('youtube', 'YouTube'),
    ('tiktok', 'TikTok'),
    ('website', 'Site personnel'),
]


class SocialLink(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=20, choices=SOCIAL_PLATFORM_CHOICES)
    url = models.URLField()

    class Meta:
        unique_together = ('profile', 'platform')
        ordering = ['platform']

    def __str__(self):
        return f"{self.get_platform_display()} - {self.profile}"


class Skill(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=80)
    level = models.PositiveSmallIntegerField(default=3, help_text="Niveau de 1 à 5")

    class Meta:
        ordering = ['-level', 'name']

    def __str__(self):
        return self.name


class Experience(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='experiences')
    title = models.CharField(max_length=150)
    company = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    is_current = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} @ {self.company}"


class Education(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='educations')
    degree = models.CharField(max_length=150)
    school = models.CharField(max_length=150)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} - {self.school}"
