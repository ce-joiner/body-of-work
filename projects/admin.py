from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'created', 'target_end', 'is_overdue')
    list_filter = ('owner', 'created', 'target_end')
    search_fields = ('title', 'description', 'owner__username')
    readonly_fields = ('created', 'updated')
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
    # checks if the project is overdue and displays a boolean icon in the admin list view
    def is_overdue(self, obj):
        return obj.is_overdue()
    is_overdue.boolean = True
    is_overdue.short_description = 'Overdue?'