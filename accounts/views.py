from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy

from profiles.models import Profile

from .forms import RegisterForm, StyledAuthenticationForm


def register(request):
    if request.user.is_authenticated:
        return redirect('profiles:dashboard')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            Profile.objects.get_or_create(user=user, defaults={'email_public': user.email})
            login(request, user)
            return redirect('profiles:onboarding')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


class ElyonLoginView(LoginView):
    template_name = 'accounts/login.html'
    form_class = StyledAuthenticationForm
    redirect_authenticated_user = True


class ElyonLogoutView(LogoutView):
    next_page = reverse_lazy('home')