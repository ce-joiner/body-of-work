"""
views for the projects app
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
# HTTP response handling
from django.http import Http404 
# pagination for splitting large datasets into pages
from django.core.paginator import Paginator
from .models import Project 
from .forms import ProjectForm

# list all projects for current user
class ProjectListView(LoginRequiredMixin, ListView):
    model = Project
    template_name = 'projects/list.html'
    context_object_name = 'projects'
    paginate_by = 10  # Number of projects per page

    #only show projects owned by the current user
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user).select_related('owner')
    
    # extends parent's context data to include total projects count
    def get_context_data(self, **kwargs):
        # get the default context from ListView
        context = super().get_context_data(**kwargs)
        # counts in database without loading records
        context['total_projects'] = self.get_queryset().count()
        return context

# create a new project
class ProjectCreateView(LoginRequiredMixin, CreateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/create.html'

    def form_valid(self, form):
        # set the owner to the current user before saving
        form.instance.owner = self.request.user
        messages.success(self.request, f'Project "{form.instance.title}" created successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})
    
# view details of a specific project
class ProjectDetailView(LoginRequiredMixin, DetailView):
    model = Project
    template_name = 'projects/detail.html'
    context_object_name = 'project'

    # get the project object and ensure it belongs to the current user
    def get_object(self, queryset=None):
        obj = get_object_or_404(Project, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise Http404("You do not have permission to view this project.")
        return obj
    
# update an existing project
class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    model = Project
    form_class = ProjectForm
    template_name = 'projects/edit.html'
    context_object_name = 'project'

    # ensure user can only update their own projects
    def get_object(self, queryset=None):
        obj = get_object_or_404(Project, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise Http404("You do not have permission to edit this project.")
        return obj
    
    def form_valid(self, form):
        messages.success(self.request, f'Project "{form.instance.title}" updated successfully!')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse_lazy('projects:detail', kwargs={'pk': self.object.pk})
    
# delete a project
class ProjectDeleteView(LoginRequiredMixin, DeleteView):
    model = Project
    template_name = 'projects/confirm_delete.html'
    context_object_name = 'project'
    success_url = reverse_lazy('projects:list')

    # ensure user can only delete their own projects
    def get_object(self, queryset=None):
        obj = get_object_or_404(Project, pk=self.kwargs['pk'])
        if obj.owner != self.request.user:
            raise Http404("You do not have permission to delete this project.")
        return obj
    
    # show success message when deleting
    def delete(self, request, *args, **kwargs):
        project = self.get_object()
        project_title = project.title
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Project "{project_title}" deleted successfully!')
        return response