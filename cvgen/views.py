from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.base import ContentFile
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .models import CVTheme
from .services import build_cv_pdf


def _regenerate_if_exists(profile):
    """Si le profil a déjà un CV généré, le régénère avec la config actuelle
    (nouveau thème notamment) pour que le fichier stocké reste à jour."""
    if profile.cv_pdf:
        buffer = build_cv_pdf(profile)
        filename = f"cv_{profile.user.username}.pdf"
        profile.cv_pdf.save(filename, ContentFile(buffer.getvalue()), save=True)


@login_required
def generate_cv(request):
    profile = request.user.profile
    buffer = build_cv_pdf(profile)
    filename = f"cv_{profile.user.username}.pdf"
    profile.cv_pdf.save(filename, ContentFile(buffer.getvalue()), save=True)
    messages.success(request, "Ton CV a été généré avec succès.")
    return redirect('profiles:dashboard')


@login_required
def download_cv(request):
    profile = request.user.profile
    if profile.cv_pdf and profile.cv_pdf.storage.exists(profile.cv_pdf.name):
        profile.cv_pdf.open('rb')
        try:
            pdf_bytes = profile.cv_pdf.read()
        finally:
            profile.cv_pdf.close()
    else:
        buffer = build_cv_pdf(profile)
        pdf_bytes = buffer.getvalue()
        filename = f"cv_{profile.user.username}.pdf"
        profile.cv_pdf.save(filename, ContentFile(pdf_bytes), save=True)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="cv_{profile.user.username}.pdf"'
    return response


@login_required
def preview_cv(request):
    """Aperçu du CV dans le navigateur (ouverture inline, pas de téléchargement forcé)."""
    profile = request.user.profile
    if profile.cv_pdf and profile.cv_pdf.storage.exists(profile.cv_pdf.name):
        profile.cv_pdf.open('rb')
        try:
            pdf_bytes = profile.cv_pdf.read()
        finally:
            profile.cv_pdf.close()
    else:
        buffer = build_cv_pdf(profile)
        pdf_bytes = buffer.getvalue()
        filename = f"cv_{profile.user.username}.pdf"
        profile.cv_pdf.save(filename, ContentFile(pdf_bytes), save=True)
    response = HttpResponse(pdf_bytes, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="cv_{profile.user.username}.pdf"'
    return response


@login_required
def choose_theme(request):
    themes = CVTheme.objects.filter(is_active=True)
    return render(request, 'cvgen/choose_theme.html', {
        'themes': themes,
        'current_theme_id': request.user.profile.cv_theme_id,
    })


@login_required
def select_theme(request, pk):
    theme = get_object_or_404(CVTheme, pk=pk, is_active=True)
    profile = request.user.profile
    profile.cv_theme = theme
    profile.save(update_fields=['cv_theme'])
    _regenerate_if_exists(profile)
    messages.success(request, f"Thème « {theme.name} » sélectionné. Ton CV a été mis à jour.")
    return redirect('profiles:dashboard')


@login_required
def clear_theme(request):
    profile = request.user.profile
    profile.cv_theme = None
    profile.save(update_fields=['cv_theme'])
    _regenerate_if_exists(profile)
    messages.success(request, "Retour à la mise en page par défaut. Ton CV a été mis à jour.")
    return redirect('cvgen:choose_theme')