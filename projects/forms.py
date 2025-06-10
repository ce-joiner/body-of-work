from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects"""
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
                'class': 'form-control-file',
                'accept': 'image/*' 
            })
        }
    # validate title is not empty after stripping whitespace
    def clean_title(self):
        title = self.cleaned_data.get('title', '').strip()
        if not title:
            raise forms.ValidationError("Title cannot be empty")
        return title
    
    # validate target end is not in the past
    def clean_target_end(self):
        target_end = self.cleaned_data.get('target_end')
        if target_end and target_end < forms.fields.DateField().to_python(forms.fields.DateField().initial):
            raise forms.ValidationError("Target end date cannot be in the past")
        return target_end
