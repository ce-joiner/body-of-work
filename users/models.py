

from django.contrib.auth.models import AbstractUser
from django.db import models
from cloudinary.models import CloudinaryField


class User(AbstractUser):
    # AbstractUser includes username, password, email, first_name, last_name 

    # stores the user's profile picture (requires Pillow library)
    avatar = CloudinaryField(
        'image',
        blank=True,
        null=True,
        help_text="Profile picture",
        transformation={
            'quality': 'auto:good',
            'fetch_format': 'auto',
        }
    )

    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="Tell us about yourself"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)


# defines the metadata for the User model, defining how it should be stored in the database
class Meta:
    db_table = 'users_user'
    verbose_name = 'User'
    verbose_name_plural = 'Users'

def __str__(self):
    return self.username 

# gets the user's full name or falls back to username 
def get_full_name(self):
    if self.first_name and self.last_name:
        return f"{self.first_name} {self.last_name}"
    return self.username

# gets the user's display name, which is either first name or username (for UI)
def get_display_name(self):
    if self.first_name:
        return self.first_name
    return self.username