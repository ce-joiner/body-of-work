from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from cloudinary.models import CloudinaryField


class Project(models.Model):
    # relationships (connects to user model)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_projects'
    )
    # basic fields
    title = models.CharField(
        max_length=200,
        help_text="Project name or title"
    )
    description = models.TextField(
        blank=True,
        help_text="Project description and details"
    )
    # date feilds
    start_date = models.DateField(
        auto_now_add=True,
        help_text="When the project started"
    )
    target_end = models.DateField(
        null=True,
        blank=True,
        help_text="Target end date for the project (optional)"
    )
    # media
    cover_photo = CloudinaryField(
    'image',
    blank=True,
    null=True,
    help_text="Cover photo for the project",
    transformation={
        'quality': 'auto:good',
        'fetch_format': 'auto',
    }
)
    # timestamps
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'projects_project'
        verbose_name = 'Project'
        verbose_name_plural = 'Projects'
        ordering = ['-created']  # Newest first
        indexes = [
            # Fast lookup of user's projects ordered by creation date
            models.Index(fields=['owner', '-created']),
            # Fast lookup of all projects by creation date
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})

    def is_overdue(self):
        # Check if project is past target end date
        if self.target_end:
            return timezone.now().date() > self.target_end
        return False
    
    # Get positive number of days overdue
    def days_overdue(self):
        if self.target_end and self.is_overdue():
            delta = timezone.now().date() - self.target_end
            return delta.days
        return 0

    def days_until_target(self):
        # Calculate days until target end date
        if self.target_end:
            delta = self.target_end - timezone.now().date()
            return delta.days  # Returns integer: positive = days left, negative = days overdue
        return None


class Photo(models.Model):
    project = models.ForeignKey(
        Project, 
        on_delete=models.CASCADE, 
        related_name='photos'
    )
    title = models.CharField(max_length=200, blank=True)
    image = CloudinaryField(
        'image',
        # Cloudinary transformation options
        transformation={
            'quality': 'auto:good',
            'fetch_format': 'auto',
        }
    )
    caption = models.TextField(blank=True)
    
    # Technical metadata
    file_size = models.PositiveIntegerField(null=True, blank=True, help_text="File size in bytes")
    mime_type = models.CharField(max_length=50, blank=True)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    
    # EXIF data stored as JSON
    exif_data = models.JSONField(blank=True, null=True, help_text="Camera EXIF data")
    
    # Workflow fields
    needs_attention = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    
    # Ordering
    order_index = models.PositiveIntegerField(default=0, help_text="Display order")
    
    # Timestamps
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order_index', 'uploaded_at']
        indexes = [
            models.Index(fields=['project', 'order_index']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['needs_attention']),
            models.Index(fields=['is_featured']),
        ]
    
    def __str__(self):
        return self.title or f"Photo {self.id}"
    
    @property
    def thumbnail_url(self):
        """Generate thumbnail URL using Cloudinary transformations"""
        if self.image:
            # Cloudinary URL transformation for thumbnails
            return self.image.build_url(
                width=300,
                height=300,
                crop='fill',
                quality='auto:good',
                fetch_format='auto'
            )
        return None
    
    @property
    def natural_thumbnail_url(self):
        """Generate thumbnail URL that preserves aspect ratio using Cloudinary transformations"""
        if self.image:
            return self.image.build_url(
                width=180,
                crop='limit',
                quality=100,  # Very high quality (0-100 scale)
                format='jpg',  # Force JPEG for consistent quality
                flags='progressive'  # Progressive JPEG loading
            )
        return None

    
    # Properties - computed attributes that act like fields but generate values dynamically
    # These can be accessed in templates like {{ photo.thumbnail_url }} without parentheses
    # Will use for generating different image sizes, formatting data, and extracting metadata

    @property
    def medium_url(self):
        # Generate medium-sized URL for galleries
        if self.image:
            return self.image.build_url(
                width=800,
                height=600,
                crop='limit',
                quality='auto:good',
                fetch_format='auto'
            )
        return None
    
    @property
    def camera_info(self):
        # Extract camera information from EXIF data
        if not self.exif_data:
            return None
        
        info = {}
        exif = self.exif_data
        
        # Common EXIF fields
        if 'Image Make' in exif:
            info['make'] = exif['Image Make']
        if 'Image Model' in exif:
            info['model'] = exif['Image Model']
        if 'EXIF FocalLength' in exif:
            info['focal_length'] = exif['EXIF FocalLength']
        if 'EXIF FNumber' in exif:
            info['aperture'] = exif['EXIF FNumber']
        if 'EXIF ExposureTime' in exif:
            info['shutter_speed'] = exif['EXIF ExposureTime']
        if 'EXIF ISOSpeedRatings' in exif:
            info['iso'] = exif['EXIF ISOSpeedRatings']
        
        return info if info else None
    
    @property
    def file_size_human(self):
        # Human readable file size
        if not self.file_size:
            return "Unknown"
        
        # Start with raw bytes and convert to appropriate unit
        bytes_size = self.file_size
        
        # Try each unit until we find one where the number is less than 1024
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                # Format with 1 decimal place: "2.5 MB", "156.8 KB", etc.
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0  # Convert to next larger unit
        
        # For very large files (unlikely for photos but covers edge cases)
        return f"{bytes_size:.1f} TB"