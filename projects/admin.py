from django.contrib import admin
from django.utils.html import format_html
from .models import Project, Photo


class PhotoInline(admin.TabularInline):
    """Inline display of photos within the project admin"""
    model = Photo
    extra = 0  # Don't show extra empty forms
    fields = ('image_thumbnail', 'title', 'caption', 'is_featured', 'needs_attention', 'uploaded_at')
    readonly_fields = ('image_thumbnail', 'uploaded_at')
    ordering = ('order_index', 'uploaded_at')
    
    def image_thumbnail(self, obj):
        """Show a small thumbnail of the photo"""
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 60px; height: 60px; object-fit: cover; border-radius: 4px;" />',
                obj.thumbnail_url or obj.image.url
            )
        return "No image"
    image_thumbnail.short_description = 'Preview'

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created', 'target_end', 'is_overdue', 'photo_count')
    list_filter = ('owner', 'created', 'target_end')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created', 'updated')
    inlines = [PhotoInline]  # Add photos inline
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description', 'owner')
        }),
        ('Dates', {
            'fields': ('created', 'target_end', 'updated')
        }),
        ('Media', {
            'fields': ('cover_photo',)
        }),
    )
    
    def photo_count(self, obj):
        """Show number of photos in this project"""
        count = obj.photos.count()
        if count > 0:
            return format_html(
                '<a href="/admin/projects/photo/?project__id__exact={}">{} photo{}</a>',
                obj.id, count, 's' if count != 1 else ''
            )
        return "0 photos"
    photo_count.short_description = 'Photos'
    
    # checks if the project is overdue and displays a boolean icon in the admin list view
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue?'


@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'project_title', 'uploaded_at', 'is_featured', 'needs_attention', 'file_size_display')
    list_filter = ('project', 'is_featured', 'needs_attention', 'uploaded_at', 'mime_type')
    search_fields = ('title', 'caption', 'project__title')
    list_select_related = ('project',)  # Optimize database queries
    readonly_fields = ('uploaded_at', 'updated_at', 'file_size', 'mime_type', 'width', 'height')
    ordering = ('-uploaded_at',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'project', 'image', 'caption')
        }),
        ('Status', {
            'fields': ('is_featured', 'needs_attention', 'order_index')
        }),
        ('Technical Info', {
            'fields': ('uploaded_at', 'updated_at', 'file_size', 'mime_type', 'width', 'height'),
            'classes': ('collapse',)  # This section will be collapsed by default
        }),
    )
    
    def project_title(self, obj):
        """Display project title as a clickable link"""
        from django.urls import reverse
        from django.utils.html import format_html
        
        url = reverse("admin:projects_project_change", args=[obj.project.id])
        return format_html('<a href="{}">{}</a>', url, obj.project.title)
    project_title.short_description = 'Project'
    project_title.admin_order_field = 'project__title'  # Allow sorting by project title
    
    def file_size_display(self, obj):
        """Display file size in human readable format"""
        return obj.file_size_human
    file_size_display.short_description = 'File Size'
    
    # Add actions for bulk operations
    actions = ['mark_featured', 'unmark_featured', 'mark_attention', 'unmark_attention']
    
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} photos marked as featured.')
    mark_featured.short_description = "Mark selected photos as featured"
    
    def unmark_featured(self, request, queryset):
        updated = queryset.update(is_featured=False)
        self.message_user(request, f'{updated} photos unmarked as featured.')
    unmark_featured.short_description = "Remove featured status from selected photos"
    
    def mark_attention(self, request, queryset):
        updated = queryset.update(needs_attention=True)
        self.message_user(request, f'{updated} photos marked as needing attention.')
    mark_attention.short_description = "Mark selected photos as needing attention"
    
    def unmark_attention(self, request, queryset):
        updated = queryset.update(needs_attention=False)
        self.message_user(request, f'{updated} photos unmarked as needing attention.')
    unmark_attention.short_description = "Remove attention flag from selected photos"