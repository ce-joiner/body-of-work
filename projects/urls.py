"""
URLs for the projects app
"""
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    # For now, just a placeholder view
    # Will expand this as I build features
    path('', views.ProjectListView.as_view(), name='project_list'),
]