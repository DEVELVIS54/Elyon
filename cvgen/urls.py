from django.urls import path

from . import views

app_name = 'cvgen'

urlpatterns = [
    path('generate/', views.generate_cv, name='generate'),
    path('download/', views.download_cv, name='download'),
    path('preview/', views.preview_cv, name='preview'),
    path('themes/', views.choose_theme, name='choose_theme'),
    path('themes/<int:pk>/select/', views.select_theme, name='select_theme'),
    path('themes/clear/', views.clear_theme, name='clear_theme'),
]