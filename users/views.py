"""
Views for the users app
"""

from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.shortcuts import redirect
from django.contrib import messages
from .models import User

# login view that redirects authenticated users
class CustomLoginView(auth_views.LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        #redirects to user's project list after login
        return reverse_lazy('projects:list')
    
    def form_valid(self, form):
        messages.success(self.request, f'Welcome back, {form.get_user().get_full_name() or form.get_user().username}!')
        return super().form_valid(form)
    
#user registration view
class RegisterView(CreateView):
    model = User
    form_class = UserCreationForm
    template_name = 'users/register.html'
    success_url = reverse_lazy('users:login')

    def dispatch(self, request, *args, **kwargs):
        # redirect authenticated users to their project list
        if request.user.is_authenticated:
            messages.info(request, 'You are already registered and logged in.')
            return redirect('projects:list')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        messages.success(self.request, 'Registration successful! You can now log in.')
        return super().form_valid(form)
    
# user profile view
class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'users/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # add the current user to the context
        context['user'] = self.request.user
        # Add more profile data here later
        return context
