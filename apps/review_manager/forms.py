from django import forms
from .models import SearchSession, SessionActivity
from django.core.exceptions import ValidationError

class SessionCreateForm(forms.ModelForm):
    class Meta:
        model = SearchSession
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'placeholder': 'e.g., Diabetes Management Guidelines Review',
                'class': 'form-control',
                'required': True,
                'autofocus': True,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'placeholder': 'Brief description of your systematic review objectives (optional)',
                'class': 'form-control',
                'rows': 3,
                'maxlength': 1000
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Review Title"
        self.fields['title'].help_text = "Give your review a clear, descriptive title"
        self.fields['description'].label = "Description (Optional)"
        self.fields['description'].help_text = "Add any additional context or objectives"
    
    def save(self, commit=True, user=None):
        session = super().save(commit=False)
        if user:
            session.created_by = user
        session.status = 'draft'
        if commit:
            session.save()
            # Log creation for analytics
            SessionActivity.objects.create(
                session=session,
                action=SessionActivity.ActivityType.CREATED,
                user=user,
                description=f"Session '{session.title}' created by {user.username}."
            )
        return session


class SessionEditForm(forms.ModelForm):
    """Form for editing existing sessions (title and description only)"""
    
    class Meta:
        model = SearchSession
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
                'maxlength': 200
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'maxlength': 1000
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].label = "Review Title"
        self.fields['title'].help_text = "Update the title for your review"
        self.fields['description'].label = "Description (Optional)"
        self.fields['description'].help_text = "Update the description or objectives"
    
    def clean_title(self):
        """Validate title is not empty and not too long"""
        title = self.cleaned_data.get('title')
        if not title or not title.strip():
            raise ValidationError('Title cannot be empty.')
        
        title = title.strip()
        if len(title) > 200:
            raise ValidationError('Title cannot be longer than 200 characters.')
        
        return title
    
    def save(self, commit=True, user=None):
        """Save with activity logging"""
        session = super().save(commit=False)
        
        if commit:
            # Check if anything actually changed
            if self.has_changed():
                session.updated_by = user
                session.save()
                
                # Log the modification
                if user:
                    changed_fields = ', '.join(self.changed_data)
                    SessionActivity.objects.create(
                        session=session,
                        action=SessionActivity.ActivityType.MODIFIED,
                        user=user,
                        description=f"Session '{session.title}' updated. Changed: {changed_fields}"
                    )
        
        return session