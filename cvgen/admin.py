from django.contrib import admin, messages

from ai.services import AIServiceError

from .models import CVTheme


@admin.register(CVTheme)
class CVThemeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'is_analyzed', 'analyzed_at')
    list_filter = ('is_active',)
    readonly_fields = ('design_spec', 'analyzed_at')
    actions = ['analyze_selected']

    @admin.action(description="Analyser le style avec l'IA (palette, mise en page)")
    def analyze_selected(self, request, queryset):
        success, failed = 0, 0
        for theme in queryset:
            try:
                theme.analyze()
                success += 1
            except AIServiceError as exc:
                failed += 1
                self.message_user(request, f"{theme.name} : {exc}", level=messages.ERROR)
        if success:
            self.message_user(request, f"{success} thème(s) analysé(s) avec succès.", level=messages.SUCCESS)
        if failed:
            self.message_user(request, f"{failed} thème(s) en échec — voir détails ci-dessus.", level=messages.WARNING)