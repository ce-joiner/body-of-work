"""
URLs for the projects app
"""
from django.urls import path
from . import views

app_name = 'projects'

urlpatterns = [
    path('', views.ProjectListView.as_view(), name='list'),
    path('new/', views.ProjectCreateView.as_view(), name='create'),
    path('<int:pk>/', views.ProjectDetailView.as_view(), name='detail'),
    path('<int:pk>/edit/', views.ProjectUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.ProjectDeleteView.as_view(), name='delete'),

    # Photo management URLs
    path('<int:project_id>/photos/upload/', views.photo_upload, name='photo_upload'),
    path('photos/<int:photo_id>/', views.photo_detail, name='photo_detail'),
    path('photos/<int:photo_id>/edit/', views.photo_edit, name='photo_edit'),
    path('photos/<int:photo_id>/delete/', views.photo_delete, name='photo_delete'),
    path('<int:project_id>/photos/bulk/', views.photos_bulk_action, name='photos_bulk_action'),
]