"""
views for the projects app
"""

from django.shortcuts import render
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin


class ProjectListView(LoginRequiredMixin, ListView):
    """ placeholder project list view """
    template_name = 'projects/project_list.html'
    context_object_name = 'projects'

    def get_queryset(self):
        # Placeholder for actual project retrieval logic
        return []  # Replace with actual query to fetch projects from the database

