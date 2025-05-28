import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model for Thesis Grey researchers.
    Extends Django's AbstractUser with UUID primary key and custom timestamps.
    """
    # Override the id field to use UUID
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text="Unique identifier for the user"
    )
    
    # Override email to make it unique but optional
    email = models.EmailField(
        unique=True, 
        null=True, 
        blank=True,
        help_text="Email address (optional but must be unique if provided)"
    )
    
    # Override the default timestamps to match Prisma schema naming
    created_at = models.DateTimeField(
        auto_now_add=True, 
        db_column='createdAt',
        help_text="Timestamp when the user account was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        db_column='updatedAt',
        help_text="Timestamp when the user account was last updated"
    )
    
    # Hide the default date_joined field from forms/serializers
    # We'll use created_at instead
    date_joined = None
    
    class Meta:
        db_table = 'User'  # Match Prisma's table naming convention
        db_table_comment = 'User accounts for Thesis Grey researchers'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        """String representation of the user."""
        return self.username
    
    def get_full_name(self):
        """Return the user's full name or username if name not provided."""
        full_name = super().get_full_name()
        return full_name if full_name.strip() else self.username

    def save(self, *args, **kwargs):
        if self.email == '':
            self.email = None
        super().save(*args, **kwargs)
