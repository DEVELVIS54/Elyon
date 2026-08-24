from io import BytesIO

from django.db import models


class CVTheme(models.Model):
    """Un thème de CV : une image de référence choisie par l'admin, que l'IA
    analyse pour en extraire une fiche de style (palette, typographie, mise
    en page) utilisée ensuite pour générer le CV final."""

    name = models.CharField(max_length=100)
    reference_image = models.ImageField(upload_to='cvgen/themes/')
    description = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True, help_text="Visible dans le catalogue proposé aux utilisateurs.")

    design_spec = models.JSONField(blank=True, null=True)
    analyzed_at = models.DateTimeField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def is_analyzed(self):
        return bool(self.design_spec)

    def analyze(self):
        """Appelle l'IA vision pour extraire la fiche de style de l'image
        de référence, et la sauvegarde. Lève ai.services.AIServiceError en
        cas d'échec (clé API manquante, erreur réseau...)."""
        from django.utils import timezone
        from PIL import Image
        from ai.services import analyze_theme_image

        self.reference_image.open('rb')
        try:
            image_bytes = self.reference_image.read()
        finally:
            self.reference_image.close()

        # Détection fiable du vrai format d'image (le champ content_type
        # n'est plus disponible une fois le fichier réouvert depuis le
        # disque — on ne peut pas se fier à l'extension du nom de fichier).
        try:
            with Image.open(BytesIO(image_bytes)) as img:
                pillow_format = (img.format or 'JPEG').upper()
        except Exception:
            pillow_format = 'JPEG'
        content_type = f"image/{'jpeg' if pillow_format == 'JPEG' else pillow_format.lower()}"

        spec = analyze_theme_image(image_bytes, content_type)
        self.design_spec = spec
        self.analyzed_at = timezone.now()
        self.save(update_fields=['design_spec', 'analyzed_at'])
        return spec