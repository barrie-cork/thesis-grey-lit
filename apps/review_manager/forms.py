from django import forms
from .models import SearchSession, SessionActivity

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
                activity_type=SessionActivity.ActivityType.CREATED,
                performed_by=user,
                description=f"Session '{session.title}' created by {user.username}."
            )
        return session