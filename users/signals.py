# users/signals.py
"""
Django Signals for User Avatar Cleanup in Cloudinary
"""

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import User
import cloudinary.uploader
import logging

logger = logging.getLogger(__name__)


@receiver(post_delete, sender=User)
def delete_user_avatar_from_cloudinary(sender, instance, **kwargs):
    """
     When a User record is deleted from the database
     Delete the user's avatar from Cloudinary
    """
    if instance.avatar:
        try:
            public_id = instance.avatar.public_id
            if public_id:
                result = cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted user avatar from Cloudinary: {public_id}, result: {result}")
        except Exception as e:
            logger.error(f"Failed to delete user avatar from Cloudinary: {e}")


@receiver(pre_save, sender=User)
def delete_old_avatar_on_update(sender, instance, **kwargs):
    """
    When a User record is about to be saved/updated - 
    If the avatar field is changing, delete the old avatar from Cloudinary
    
    This prevents orphaned files when users change their profile picture.
    """
    # Check if this is a new user being created
    if not instance.pk:
        return  # New user, no old avatar to delete
        
    try:
        # Get the current version of this user from the database
        old_instance = User.objects.get(pk=instance.pk)
        
        # Check if the avatar is actually changing
        if old_instance.avatar and old_instance.avatar != instance.avatar:
            public_id = old_instance.avatar.public_id
            
            if public_id:
                # Delete the old avatar since it's being replaced
                cloudinary.uploader.destroy(public_id)
                logger.info(f"Deleted old user avatar from Cloudinary: {public_id}")
                
    except User.DoesNotExist:
        # This shouldn't happen, but safety first
        pass
    except Exception as e:
        logger.error(f"Failed to delete old user avatar from Cloudinary: {e}")