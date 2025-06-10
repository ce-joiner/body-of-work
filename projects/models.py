from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Project(models.Model):
    # relationships
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
    cover_photo = models.ImageField(
        upload_to='project_covers/',
        blank=True,
        null=True,
        help_text="Cover photo for the project"
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
            models.Index(fields=['owner', '-created']),
            models.Index(fields=['-created']),
        ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('projects:detail', kwargs={'pk': self.pk})

    def is_overdue(self):
        """Check if project is past target end date"""
        if self.target_end:
            return timezone.now().date() > self.target_end
        return False

    def days_until_target(self):
        """Calculate days until target end date"""
        if self.target_end:
            delta = self.target_end - timezone.now().date()
            return delta.days  # Returns integer: positive = days left, negative = days overdue
        return None

# Signal handlers for automatic file cleanup
@receiver(post_delete, sender=Project)
def delete_project_cover_photo(sender, instance, **kwargs):
    # Delete cover photo file when project is deleted
    if instance.cover_photo:
        if os.path.isfile(instance.cover_photo.path):
            os.remove(instance.cover_photo.path)


@receiver(pre_save, sender=Project)
def delete_old_cover_photo_on_update(sender, instance, **kwargs):
    # Delete old cover photo when a new one is uploaded
    if not instance.pk:
        return  # New instance, no old file to delete
    
    try:
        old_project = Project.objects.get(pk=instance.pk)
        old_cover_photo = old_project.cover_photo
    except Project.DoesNotExist:
        return  # Object doesn't exist yet
    
    # Check if cover photo has changed
    new_cover_photo = instance.cover_photo
    if old_cover_photo and old_cover_photo != new_cover_photo:
        if os.path.isfile(old_cover_photo.path):
            os.remove(old_cover_photo.path)