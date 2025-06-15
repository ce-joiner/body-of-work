
# views for the projects app

# Standard library imports
import json

# Django core imports
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db import transaction
from django.http import Http404, JsonResponse, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView

# Local app imports
from .models import Project, Photo
from .forms import ProjectForm, PhotoUploadForm, BulkPhotoUploadForm, PhotoEditForm, PhotoBulkActionForm
from .utils import process_uploaded_photo, handle_upload_error


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
    
# handle photo uploads for a project (single and bulk)
@login_required
@csrf_protect
def photo_upload(request, project_id):
    project = get_object_or_404(Project, id=project_id)
    #check if the user owns the project (will add collaborator support later)
    if project.owner != request.user:
        messages.error(request, "You do not have permission to upload photos for this project.")
        return redirect('projects:detail', pk=project_id)
    
    if request.method == 'GET':
        # show the upload form
        form = PhotoUploadForm()
        context = {
            'project': project,
            'form': form,
        }
        return render(request, 'projects/photo_upload.html', context)
    
    elif request.method == 'POST':
        # handle photo uploads
        return _process_photo_uploads(request, project)
    
# helper function to handle photo uploads, determines if it's single or bulk upload
def _process_photo_uploads(request, project):
    # Get files using correct field names and add bulk validation
    uploaded_files = request.FILES.getlist('photos')  # For bulk upload
    single_file = request.FILES.get('image')  # For single upload (corrected from 'photo')
    
    
    if single_file and not uploaded_files:
        #single upload via PhotoUploadForm
        files_to_process = [single_file]
        upload_type = 'single'
        form = PhotoUploadForm(request.POST, request.FILES)
        
    elif uploaded_files:
        #bulk upload via BulkPhotoUploadForm
        files_to_process = uploaded_files
        upload_type = 'bulk'
        form = BulkPhotoUploadForm(request.POST, request.FILES)
        
       
        # ADDED: Manual validation for bulk files since form can't handle multiple files
        if len(files_to_process) > 20:
            messages.error(request, "Too many files selected. Maximum allowed: 20")
            return redirect('projects:photo_upload', project_id=project.id)
            
    else:
        # no files to upload
        messages.error(request, "Select at least one photo to upload.")
        return redirect('projects:photo_upload', project_id=project.id)
        

         # form validation
    
    if upload_type == 'single':
        if not form.is_valid():
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
            return redirect('projects:photo_upload', project_id=project.id)
        
    # Only validate form for single uploads (bulk validation handled above)
    if upload_type == 'single' and not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        return redirect('projects:photo_upload', project_id=project.id)
        
    # Process each uploaded file
    successful_uploads = []
    failed_uploads = []

    # Use database transaction to ensure data consistency
    # this will rollback if any upload fails
    with transaction.atomic():
        for uploaded_file in files_to_process:
            try:
                # Process the uploaded photo and get metadata
                photo_data = process_uploaded_photo(uploaded_file, project)
                # Create the Photo object
                photo = Photo.objects.create(
                    project=project,
                    image=uploaded_file,  # Cloudinary handles the actual upload
                    title=photo_data['title'],
                    file_size=photo_data['file_size'],
                    mime_type=photo_data['mime_type'],
                    width=photo_data['width'],
                    height=photo_data['height'],
                    exif_data=photo_data['exif_data'],
                    # If single upload, get additional fields from form
                    caption=form.cleaned_data.get('caption', '') if upload_type == 'single' else '',
                )
                successful_uploads.append({
                    'id': photo.id,
                    'title': photo.title,
                    'thumbnail_url': photo.thumbnail_url,
                    'filename': uploaded_file.name
                })
                    
            except ValidationError as e:
                # Handle validation errors
                error_message = handle_upload_error(e, uploaded_file.name)
                failed_uploads.append({
                    'filename': uploaded_file.name,
                    'error': error_message
                })

            except Exception as e:
                # Handle unexpected errors
                error_message = handle_upload_error(e, uploaded_file.name)
                failed_uploads.append({
                    'filename': uploaded_file.name,
                    'error': error_message
                })

    # Prepare response messages
    success_count = len(successful_uploads)
    failure_count = len(failed_uploads)

    if success_count > 0:
        if success_count == 1:
            messages.success(request, f'Photo "{successful_uploads[0]["title"]}" uploaded successfully!')
        else:
            messages.success(request, f'{success_count} photos uploaded successfully!')

    if failure_count > 0:
        for failed in failed_uploads:
            messages.error(request, f"Failed to upload '{failed['filename']}': {failed['error']}")
            messages.error(request, f"Failed to upload '{failed['filename']}': {failed['error']}")

    # Handle AJAX requests (for dynamic uploads without page reload)
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': success_count > 0,
            'successful_uploads': successful_uploads,
            'failed_uploads': failed_uploads,
            'total_success': success_count,
            'total_failed': failure_count,
        })
    
    # Redirect to project detail page after upload
    return redirect('projects:detail', pk=project.id)

# Photo management views

# Display detailed view of a single photo with metadata.
@login_required
def photo_detail(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    # check permission
    if photo.project.owner != request.user:
        messages.error(request, "You do not have permission to view this photo.")
        return redirect('projects:detail', pk=photo.project.id)
        
    context = {
        'photo': photo,
        'project': photo.project,
        'camera_info': photo.camera_info,  # Uses the property defined in models
    }
    return render(request, 'projects/photo_detail.html', context)
      
# Edit photo metadata
@login_required
@csrf_protect
def photo_edit(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)

    if photo.project.owner != request.user:
        messages.error(request, "You do not have permission to edit this photo.")
        return redirect('projects:detail', pk=photo.project.id)
        
    if request.method == 'POST':
        form = PhotoEditForm(request.POST, instance=photo)
        if form.is_valid():
            form.save()
            messages.success(request, f"Updated '{photo.title}' successfully!")
            return redirect('projects:photo_detail', photo_id=photo.id)
        else:
            messages.error(request, "Please correct the errors.")
    else:
        form = PhotoEditForm(instance=photo)

    context = {
        'form': form,
        'photo': photo,
        'project': photo.project,
    }
    return render(request, 'projects/photo_edit.html', context)
        
# Delete a photo from a project
@login_required
@csrf_protect
def photo_delete(request, photo_id):
    photo = get_object_or_404(Photo, id=photo_id)
    
    # Check permission
    if photo.project.owner != request.user:
        messages.error(request, "You don't have permission to delete this photo.")
        return redirect('projects:detail', pk=photo.project.id)
    
    if request.method == 'POST':
        photo_title = photo.title
        project_id = photo.project.id
        
        # Delete the photo (Cloudinary cleanup happens automatically)
        photo.delete()
        
        messages.success(request, f"Deleted '{photo_title}' successfully!")
        return redirect('projects:detail', pk=project_id)
    
    context = {
        'photo': photo,
        'project': photo.project,
    }
    return render(request, 'projects/photo_confirm_delete.html', context)
   
# Bulk actions for photos in a project
@login_required
@csrf_protect
@require_POST
def photos_bulk_action(request, project_id):
    project = get_object_or_404(Project, id=project_id)

    if project.owner != request.user:
        return HttpResponseForbidden("You do not have permission to modify photos in this project.")

    form = PhotoBulkActionForm(request.POST)
    if not form.is_valid():
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(request, f"{field}: {error}")
        return redirect('projects:detail', pk=project_id)

    action = form.cleaned_data['action']
    photo_ids = form.cleaned_data['photo_ids']

    # Get the photos and verify they belong to this project
    photos = Photo.objects.filter(id__in=photo_ids, project=project)

    if not photos.exists():
        messages.error(request, "No valid photos selected.")
        return redirect('projects:detail', pk=project_id)

    # Perform the bulk action
    with transaction.atomic():
        if action == 'delete':
            count = photos.count()
            photos.delete()
            messages.success(request, f"Permanently deleted {count} photo{'s' if count != 1 else ''}.")

        elif action == 'flag':
            count = photos.update(needs_attention=True)
            messages.success(request, f"Flagged {count} photo{'s' if count != 1 else ''} for attention.")

        elif action == 'unflag':
            count = photos.update(needs_attention=False)
            messages.success(request, f"Removed attention flag from {count} photo{'s' if count != 1 else ''}.")

        elif action == 'feature':
            count = photos.update(is_featured=True)
            messages.success(request, f"Marked {count} photo{'s' if count != 1 else ''} as featured.")
            
        elif action == 'unfeature':
            count = photos.update(is_featured=False)
            messages.success(request, f"Removed featured status from {count} photo{'s' if count != 1 else ''}.")

    return redirect('projects:detail', pk=project.id)