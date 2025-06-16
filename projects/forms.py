from django import forms
from .models import Project, Photo
from .utils import validate_image_file
from django.core.exceptions import ValidationError
from cloudinary.models import CloudinaryResource

# Form for creating and editing projects
class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['title', 'description', 'target_end', 'cover_photo']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Describe your project',
                'rows': 4
            }),
            'target_end': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'cover_photo': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*' 
            })
        }
    
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty")
        return title
    
    def clean_target_end(self):
        target_end = self.cleaned_data.get('target_end')
        # Fixed the date validation logic
        from django.utils import timezone
        if target_end and target_end < timezone.now().date():
            raise forms.ValidationError("Target end date cannot be in the past")
        return target_end
    
    def clean_cover_photo(self):
        cover_photo = self.cleaned_data.get('cover_photo')
        
        # If cover_photo is None or False, it means no new file was uploaded
        # This keeps the existing photo (for editing)
        if not cover_photo:
            return cover_photo
            
        # allows existing Cloudinary resources to pass through without validation (for editing)
        if isinstance(cover_photo, CloudinaryResource):
            return cover_photo
            
        # Only validate new file uploads
        if hasattr(cover_photo, 'size') and hasattr(cover_photo, 'content_type'):
            try:
                validate_image_file(cover_photo)
            except ValidationError as e:
                raise forms.ValidationError(f"Cover photo error: {e}")
        return cover_photo

# Form for single photo uploads
class PhotoUploadForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'image', 'caption']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photo title (auto-generated if left blank)'
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/jpeg,image/jpg,image/png,image/webp,image/tiff,image/heic',
                'id': 'single-photo-input'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Add a caption for this photo...',
                'rows': 3
            })
        }
    
    def clean_image(self):
        # Validate the uploaded image file
        image = self.cleaned_data.get('image')
        if image:
            try:
                validate_image_file(image)
            except ValidationError as e:
                raise forms.ValidationError(str(e))
        return image

# Form for bulk photo uploads - handle multiple files properly
class BulkPhotoUploadForm(forms.Form):
    def __init__(self, *args, **kwargs):
        # Initialize the form with validation limits.
        self.max_files = kwargs.pop('max_files', 20)
        self.max_file_size = kwargs.pop('max_file_size', 50 * 1024 * 1024)  # 50MB
        super().__init__(*args, **kwargs)
    
    def clean(self):
        # Validate all uploaded photos.
        # This method handles the multiple file validation since Django's FileInput widget doesn't natively support multiple files.
        
        cleaned_data = super().clean()
        
        # Get files from request.FILES.getlist('photos') in the view
        # handle this in the view and just validate here
        
        return cleaned_data

# Form for editing photo metadata after upload
class PhotoEditForm(forms.ModelForm):
    class Meta:
        model = Photo
        fields = ['title', 'caption', 'needs_attention', 'is_featured']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Photo title...'
            }),
            'caption': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Photo caption...',
                'rows': 4
            }),
            'needs_attention': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'is_featured': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }
        labels = {
            'needs_attention': 'Mark this photo for attention',
            'is_featured': 'Feature this photo in project gallery',
        }

# Form for bulk actions on multiple photos
class PhotoBulkActionForm(forms.Form):
    ACTION_CHOICES = [
        ('', 'Select action...'),
        ('delete', 'Delete photos permanently'),
        ('feature', 'Mark as featured'),
        ('unfeature', 'Remove featured status'),
        ('flag', 'Mark needs attention'),
        ('unflag', 'Remove attention flag'),
    ]
    
    action = forms.ChoiceField(
        choices=ACTION_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'bulk-action-select'
        }),
        help_text='Choose an action to apply to selected photos'
    )
    
    # Hidden field to store comma-separated photo IDs
    photo_ids = forms.CharField(
        widget=forms.HiddenInput(attrs={
            'id': 'bulk-photo-ids'
        }),
        required=False
    )
    
    def clean_action(self):
        # Validate that an action was selected
        action = self.cleaned_data.get('action')
        if not action:
            raise forms.ValidationError("Please select an action.")
        return action
    
    def clean_photo_ids(self):
        # Convert comma-separated photo IDs to a list of integers.
        photo_ids = self.cleaned_data.get('photo_ids', '')
        if not photo_ids:
            raise forms.ValidationError("Please select photos first.")
        
        try:
            # Split by comma, strip whitespace, convert to int, filter out empty strings
            ids = [int(pid.strip()) for pid in photo_ids.split(',') if pid.strip()]
            if not ids:
                raise forms.ValidationError("No valid photo IDs provided.")
            return ids
        except ValueError:
            raise forms.ValidationError("Invalid photo ID format.")

# Form for photo search and filtering (for future use - did not get to fully flesh this out yet)
class PhotoFilterForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search photos by title or caption...'
        })
    )
    
    needs_attention = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Only photos needing attention'
    )
    
    is_featured = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Only featured photos'
    )
    
    # Date range filtering
    uploaded_after = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Uploaded after'
    )
    
    uploaded_before = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Uploaded before'
    )

# Form for reordering photos (used with drag & drop)
class PhotoReorderForm(forms.Form):
    photo_order = forms.CharField(
        widget=forms.HiddenInput(),
        help_text='JSON array of photo IDs in new order'
    )
    
    def clean_photo_order(self):
        # Validate and parse the photo order data.
      
        import json
        
        order_data = self.cleaned_data.get('photo_order', '')
        if not order_data:
            raise forms.ValidationError("No order data provided.")
        
        try:
            # Parse JSON string to Python list
            order_list = json.loads(order_data)
            
            # Validate it's a list of integers
            if not isinstance(order_list, list):
                raise forms.ValidationError("Order data must be a list.")
            
            # Convert all items to integers and validate
            validated_order = []
            for item in order_list:
                try:
                    validated_order.append(int(item))
                except (ValueError, TypeError):
                    raise forms.ValidationError(f"Invalid photo ID: {item}")
            
            return validated_order
            
        except json.JSONDecodeError:
            raise forms.ValidationError("Invalid JSON format for order data.")

# Form validation helpers to handle image uploads
def validate_image_upload_form(form_class, request):
    form = form_class(request.POST, request.FILES)
    is_valid = form.is_valid()
    
    errors = []
    if not is_valid:
        for field, field_errors in form.errors.items():
            for error in field_errors:
                errors.append(f"{field}: {error}")
    
    return form, is_valid, errors