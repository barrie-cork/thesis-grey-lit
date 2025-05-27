from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

class SignUpForm(UserCreationForm):
    """
    Form for user registration. Extends UserCreationForm to include email field
    and custom validation.
    """
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email (optional)'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add form-control class to password fields
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
    
    def clean_email(self):
        """
        Validate that the email is unique if provided.
        """
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise ValidationError('A user with this email already exists.')
        return email

class ProfileForm(UserChangeForm):
    """
    Form for updating user profile. Extends UserChangeForm but removes
    the password field and adds custom validation.
    """
    password = None  # Remove the password field
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'})
        }
    
    def clean_email(self):
        """
        Validate that the email is unique if provided, excluding the current user.
        """
        email = self.cleaned_data.get('email')
        if email:
            existing_users = User.objects.filter(email=email).exclude(pk=self.instance.pk)
            if existing_users.exists():
                raise ValidationError('A user with this email already exists.')
        return email 