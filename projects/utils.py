"""
Image processing utilities for photo uploads.

Provides secure image validation, EXIF metadata extraction, and photo processing.
Key functions: validate_image_file(), extract_exif_data(), get_image_dimensions(),
process_uploaded_photo(). Includes security validation and error handling.
"""

from PIL import Image
from PIL.ExifTags import TAGS
import exifread
from django.core.exceptions import ValidationError
from django.conf import settings
from cloudinary.models import CloudinaryResource
import io
import logging

# __name__ = 'projects.utils' (the full module path)
# Creates a logger named 'projects.utils'
logger = logging.getLogger(__name__)

# Validate uploaded image file for type, size, and basic integrity


def validate_image_file(uploaded_file):
     # If it's an existing Cloudinary resource, skip validation
    if isinstance(uploaded_file, CloudinaryResource):
        return True
    
    # If it's a string (URL), also skip validation (existing image)
    if isinstance(uploaded_file, str):
        return True
    
    # Only validate actual file uploads
    if not hasattr(uploaded_file, 'size') or not hasattr(uploaded_file, 'content_type'):
        # If it doesn't have these attributes, it might be an existing resource
        return True
    
    # Check file size
    if uploaded_file.size > settings.MAX_UPLOAD_SIZE:
        raise ValidationError(
            f"File too large. Maximum size is {settings.MAX_UPLOAD_SIZE // (1024*1024)}MB. "
            f"Your file is {uploaded_file.size // (1024*1024)}MB."
        )
    
    

    # Check MIME type
    # Instead of generic error, shows specific message:
    # "Unsupported file type: image/bmp. Allowed types: JPEG, PNG, GIF, WEBP"
    if uploaded_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
        allowed_types = ', '.join([t.split('/')[-1].upper()
                                  for t in settings.ALLOWED_IMAGE_TYPES])
        raise ValidationError(
            f"Unsupported file type: {uploaded_file.content_type}. "
            f"Allowed types: {allowed_types}"
        )

    # Try to open the image to validate it's actually an image
    try:
        uploaded_file.seek(0)  # Reset file pointer
        with Image.open(uploaded_file) as img:
            # Verify it's a valid image
            img.verify()
        uploaded_file.seek(0)  # Reset file pointer again
    except Exception as e:
        raise ValidationError(f"Invalid or corrupted image file: {str(e)}")

    return True

# Extract EXIF data from uploaded image
def extract_exif_data(uploaded_file):
    try:
        uploaded_file.seek(0)

        # Use exifread for comprehensive EXIF extraction
        tags = exifread.process_file(uploaded_file, details=False)

        exif_dict = {}

        # Convert EXIF tags to a serializable dictionary
        for tag, value in tags.items():
            # Skip binary data and thumbnails
            if tag not in ['JPEGThumbnail', 'TIFFThumbnail', 'Filename']:
                try:
                    # Convert to string for JSON serialization
                    exif_dict[tag] = str(value)
                except Exception as e:
                    # Skip problematic tags
                    logger.warning(f"Failed to process EXIF tag {tag}: {e}")
                    continue

        uploaded_file.seek(0)  # Reset file pointer

        return exif_dict if exif_dict else None

    except Exception as e:
        logger.warning(f"EXIF extraction failed: {e}")
        uploaded_file.seek(0)  # Ensure file pointer is reset
        return None

# Get image width and height
def get_image_dimensions(uploaded_file):
    """
    Get image width and height.
    Returns None for existing Cloudinary resources.
    """
    # Skip dimension extraction for existing Cloudinary resources
    if isinstance(uploaded_file, (CloudinaryResource, str)):
        return None, None
        
    # Only get dimensions from actual file uploads
    if not hasattr(uploaded_file, 'seek'):
        return None, None
        
    try:
        uploaded_file.seek(0)
        with Image.open(uploaded_file) as img:
            width, height = img.size
        uploaded_file.seek(0)
        return width, height
    except Exception as e:
        logger.warning(f"Failed to get image dimensions: {e}")
        uploaded_file.seek(0)
        return None, None

# Generate a default title from filename
def generate_photo_title(uploaded_file):
    # Handle existing Cloudinary resources
    if isinstance(uploaded_file, (CloudinaryResource, str)):
        return "Photo"
    # Handle file uploads
    if hasattr(uploaded_file, 'name') and uploaded_file.name:
        filename = uploaded_file.name
        # Remove extension and clean up
        title = filename.rsplit('.', 1)[0]
        # Replace underscores and hyphens with spaces
        title = title.replace('_', ' ').replace('-', ' ')
        # Capitalize words
        title = ' '.join(word.capitalize() for word in title.split())
        return title
    return "Untitled Photo"

# Complete processing pipeline for uploaded photo
# Returns dictionary with processed data
def process_uploaded_photo(uploaded_file, project):
    # Validate the file
    validate_image_file(uploaded_file)

    # Extract metadata
    exif_data = extract_exif_data(uploaded_file)
    width, height = get_image_dimensions(uploaded_file)
    title = generate_photo_title(uploaded_file)

    # Prepare photo data
    photo_data = {
        'title': title,
        'file_size': getattr(uploaded_file, 'size', None),
        'mime_type': getattr(uploaded_file, 'content_type', None),
        'width': width,
        'height': height,
        'exif_data': exif_data,
    }

    return photo_data

# Custom exception for image upload errors
class ImageUploadError(Exception):
    pass

# Convert various upload errors into user-friendly messages
def handle_upload_error(error, filename="Unknown"):
    if isinstance(error, ValidationError):
        return str(error)
    elif "size" in str(error).lower():
        return f"File '{filename}' is too large. Please choose a smaller image."
    elif "format" in str(error).lower() or "type" in str(error).lower():
        return f"File '{filename}' is not a supported image format."
    elif "corrupt" in str(error).lower():
        return f"File '{filename}' appears to be corrupted. Please try a different image."
    else:
        return f"Failed to upload '{filename}'. Please try again or choose a different image."
