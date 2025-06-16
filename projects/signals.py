# projects/signals.py
"""
Django Signals for Cloudinary File Cleanup

Django signals are hooks that get triggered when certain database operations occur.
This file ensures that when records are deleted or updated in the database, 
the corresponding files in Cloudinary cloud storage are also cleaned up.

Without these signals, deleted photos would remain in Cloudinary forever,
consuming storage space and potentially costing money.
"""

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Project, Photo
import cloudinary.uploader
import logging

# Set up logging to track what files are being deleted from Cloudinary
logger = logging.getLogger(__name__)


@receiver(post_delete, sender=Photo)
def delete_photo_from_cloudinary(sender, instance, **kwargs):
    """
    This happens when:
    - User deletes a single photo
    - User deletes a project (cascade deletes all photos)
    - Admin deletes photos from Django admin
    """
    # Check if the photo instance actually has an image file
    if instance.image:
        try:
            # Get the unique identifier that Cloudinary uses for this file
            # public_id is like a filename in Cloudinary (e.g., "photos/abc123")
            public_id = instance.image.public_id
            
            if public_id:
                # Tell Cloudinary to permanently delete this file
                result = cloudinary.uploader.destroy(public_id)
                # Log success for debugging/monitoring
                logger.info(f"Deleted photo from Cloudinary: {public_id}, result: {result}")
                
        except Exception as e:
            # If something goes wrong, log the error but don't crash the app
            # The database deletion still succeeds even if Cloudinary cleanup fails
            logger.error(f"Failed to delete photo from Cloudinary: {e}")


@receiver(post_delete, sender=Project)
def delete_project_cover_from_cloudinary(sender, instance, **kwargs):
    """
    This only handles the cover photo. Individual photos are handled
    by the delete_photo_from_cloudinary signal above (they cascade delete).
    """
    # Check if the project has a cover photo
    if instance.cover_photo:
        try:
            # Same process as above - get the public_id and delete from Cloudinary
            public_id = instance.cover_photo.public_id
            
            if public_id:
                result = cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted project cover from Cloudinary: {public_id}, result: {result}")
                
        except Exception as e:
            logger.error(f"Failed to delete project cover from Cloudinary: {e}")


@receiver(pre_save, sender=Photo)
def delete_old_photo_on_update(sender, instance, **kwargs):
    """
    If the image field is changing, delete the old image from Cloudinary
    
    This prevents orphaned files when users replace a photo with a new one.
    Uses pre_save (before saving) so you can still access the old data.
    """
    # Check if this is a new photo being created (no primary key yet)
    if not instance.pk:
        return  # New instance, nothing to delete
        
    try:
        # Get the current version of this photo from the database
        old_instance = Photo.objects.get(pk=instance.pk)
        
        # Check if the image field is actually changing
        # (old_instance.image != instance.image means user uploaded a new file)
        if old_instance.image and old_instance.image != instance.image:
            public_id = old_instance.image.public_id
            
            if public_id:
                # Delete the old image since it's being replaced
                cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted old photo from Cloudinary: {public_id}")
                
    except Photo.DoesNotExist:
        # This shouldn't happen, but if it does, just continue
        pass
    except Exception as e:
        logger.error(f"Failed to delete old photo from Cloudinary: {e}")


@receiver(pre_save, sender=Project)
def delete_old_cover_on_update(sender, instance, **kwargs):
    """
    If the cover_photo field is changing, delete the old cover from Cloudinary
    
    Same logic as delete_old_photo_on_update but for project cover photos.
    """
    # Check if this is a new project being created
    if not instance.pk:
        return  # New project, no old cover to delete
        
    try:
        # Get the current version of this project from the database
        old_instance = Project.objects.get(pk=instance.pk)
        
        # Check if the cover photo is actually changing
        if old_instance.cover_photo and old_instance.cover_photo != instance.cover_photo:
            public_id = old_instance.cover_photo.public_id
            
            if public_id:
                # Delete the old cover photo since it's being replaced
                cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted old project cover from Cloudinary: {public_id}")
                
    except Project.DoesNotExist:
        # This shouldn't happen, but safety first
        pass
    except Exception as e:
        logger.error(f"Failed to delete old project cover from Cloudinary: {e}")


"""
IMPORTANT NOTES:

1. These signals are automatically triggered by Django - you don't call them directly
2. They run every time the specified database operations occur
3. If Cloudinary deletion fails, the app continues working (graceful degradation)
4. The signals must be registered when Django starts (handled in apps.py)
5. post_delete runs AFTER the database record is deleted
6. pre_save runs BEFORE the database record is saved/updated
7. Always use try/except blocks to prevent signal failures from breaking the app

"""