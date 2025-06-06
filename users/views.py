"""
Views for the users app
"""

from django.shortcuts import render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm

class RegisterView(CreateView):
    """ placeholder user registation view"""
    form_class = UserCreationForm
    template_name = 'users/register.html'   
    success_url = reverse_lazy('users:login')


class ProfileView(LoginRequiredMixin, TemplateView):
    """ placeholder user profile view """
    template_name = 'users/profile.html'