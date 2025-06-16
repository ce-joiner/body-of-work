
# Views for the users app

from django.contrib.auth import views as auth_views
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView, UpdateView, DeleteView
from django.shortcuts import redirect
from django.contrib import messages
from .forms import ProfileEditForm, UserCreationForm
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

class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = ProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile')

    def get_object(self):
        # Always return the current user
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Your profile has been updated successfully!')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'Please correct the errors below.')
        return super().form_invalid(form)
    
class AccountDeleteView(LoginRequiredMixin, DeleteView):
    model = User
    template_name = 'users/confirm_delete_account.html'
    success_url = reverse_lazy('home')  # Redirect to home after deletion

    def get_object(self):
        # Always return the current user
        return self.request.user
    
    def delete(self, request, *args, **kwargs):
        user = self.get_object()
        username = user.username
        
        # Delete the user (cascades to projects/photos, signals handle Cloudinary)
        response = super().delete(request, *args, **kwargs)
        
        # Add success message for home page
        messages.success(request, f'Account "{username}" has been permanently deleted.')
        return response