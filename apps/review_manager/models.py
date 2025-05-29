from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

class SearchSession(models.Model):
    """
    Model to track and manage literature review search sessions.
    Each session represents a distinct literature review process.
    Includes Phase 2 collaboration fields (unused in Phase 1).
    
    NOTE: PIC framework fields (Population, Interest, Context) are handled
    by the Search Strategy app, not here.
    """
    
    class Status(models.TextChoices):
        DRAFT = 'draft', _('Draft')
        STRATEGY_READY = 'strategy_ready', _('Strategy Ready')
        EXECUTING = 'executing', _('Executing Searches')
        PROCESSING = 'processing', _('Processing Results')
        READY_FOR_REVIEW = 'ready_for_review', _('Ready for Review')
        IN_REVIEW = 'in_review', _('Under Review')
        COMPLETED = 'completed', _('Completed')
        FAILED = 'failed', _('Failed')
        ARCHIVED = 'archived', _('Archived')
    
    class Visibility(models.TextChoices):
        PRIVATE = 'private', _('Private')
        TEAM = 'team', _('Team')
        PUBLIC = 'public', _('Public')

    # Core session information
    title = models.CharField(
        max_length=200, 
        help_text=_('Title of the search session')
    )
    description = models.TextField(
        blank=True, 
        help_text=_('Detailed description of the search session')
    )
    
    # Status and workflow
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        help_text=_('Current status of the search session')
    )
    
    # Ownership and permissions (Phase 1)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_sessions',
        help_text=_('User who created this search session')
    )
    
    # Phase 2 collaboration fields (unused in Phase 1)
    # team = models.ForeignKey('teams.Team', null=True, blank=True, on_delete=models.SET_NULL)
    # collaborators = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True, related_name='collaborative_sessions')
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PRIVATE,
        help_text=_('Who can view this session (Phase 2 feature)')
    )
    permissions = models.JSONField(
        default=dict, 
        blank=True, 
        help_text=_('Permission settings (Phase 2 feature)')
    )
    
    # Audit fields
    created_at = models.DateTimeField(
        auto_now_add=True, 
        help_text=_('When this session was created')
    )
    updated_at = models.DateTimeField(
        auto_now=True, 
        help_text=_('When this session was last updated')
    )
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='updated_sessions',
        help_text=_('User who last updated this session')
    )
    
    # Optional workflow timestamps
    start_date = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_('When this session was started (moved beyond draft)')
    )
    completed_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this session was completed')
    )
    
    class Meta:
        ordering = ['-updated_at']
        verbose_name = _('Search Session')
        verbose_name_plural = _('Search Sessions')
        indexes = [
            # Performance optimization indexes
            models.Index(fields=['created_by', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['updated_at']),
            models.Index(fields=['status']),
            # Ready for Phase 2 collaboration
            # models.Index(fields=['team', 'status']),
        ]
        # Note: Title validation handled at form level for better UX
        
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
    
    def can_transition_to(self, new_status):
        """
        Validates if the session can transition to the given status
        using the SessionStatusManager.
        """
        manager = SessionStatusManager()
        current_status_value = self.status
        new_status_value = new_status.value if hasattr(new_status, 'value') else new_status
        
        return manager.can_transition(current_status_value, new_status_value)
    
    def get_absolute_url(self):
        """Get the URL for this session's detail page"""
        return reverse('review_manager:session_detail', kwargs={'session_id': self.pk})
    
    @property
    def stats(self):
        """
        Get basic statistics for this session.
        This will be expanded when other apps are implemented.
        """
        # Base stats - will be enhanced by other apps
        base_stats = {
            'session_id': self.pk,
            'status': self.status,
            'created_days_ago': (timezone.now() - self.created_at).days,
        }
        
        # These will be populated by other apps:
        # - Search Strategy app will add: strategy_terms_count, queries_defined
        # - SERP Execution app will add: executions_count, results_found
        # - Review Results app will add: results_reviewed, included_count, excluded_count
        
        return base_stats
    
    def can_be_deleted(self):
        """Check if this session can be deleted (only draft sessions)"""
        return self.status == self.Status.DRAFT
    
    def can_be_archived(self):
        """Check if this session can be archived (only completed sessions)"""
        return self.status == self.Status.COMPLETED
    
    def can_be_duplicated(self):
        """Check if this session can be duplicated (any non-draft status)"""
        return self.status != self.Status.DRAFT


class SessionStatusManager:
    """
    Manages status transitions with validation and logging.
    Enforces the workflow defined in the PRD.
    """
    
    ALLOWED_TRANSITIONS = {
        'draft': ['strategy_ready'],
        'strategy_ready': ['executing', 'draft'],
        'executing': ['processing', 'failed'],
        'processing': ['ready_for_review', 'failed'],
        'ready_for_review': ['in_review'],
        'in_review': ['completed', 'ready_for_review'],
        'completed': ['archived', 'in_review'],
        'failed': ['draft', 'strategy_ready'],
        'archived': ['completed']
    }
    
    def can_transition(self, from_status, to_status):
        """
        Checks if a transition from from_status to to_status is allowed.
        
        Args:
            from_status (str): Current status
            to_status (str): Target status
            
        Returns:
            bool: True if transition is allowed, False otherwise
        """
        return to_status in self.ALLOWED_TRANSITIONS.get(from_status, [])
    
    def get_next_allowed_statuses(self, current_status):
        """Get list of statuses that can be transitioned to from current status"""
        return self.ALLOWED_TRANSITIONS.get(current_status, [])
    
    def validate_transition(self, from_status, to_status):
        """
        Validate a status transition and return error message if invalid.
        
        Returns:
            str or None: Error message if invalid, None if valid
        """
        if not self.can_transition(from_status, to_status):
            allowed = self.get_next_allowed_statuses(from_status)
            return f"Cannot transition from '{from_status}' to '{to_status}'. Allowed transitions: {allowed}"
        return None


class SessionActivity(models.Model):
    """
    Model to log activities and changes in search sessions.
    Provides an audit trail of all significant actions and status changes.
    """
    
    class ActivityType(models.TextChoices):
        CREATED = 'CREATED', _('Session Created')
        STATUS_CHANGED = 'STATUS_CHANGED', _('Status Changed')
        MODIFIED = 'MODIFIED', _('Session Modified')
        STRATEGY_DEFINED = 'STRATEGY_DEFINED', _('Search Strategy Defined')
        SEARCH_EXECUTED = 'SEARCH_EXECUTED', _('Search Executed')
        RESULTS_PROCESSED = 'RESULTS_PROCESSED', _('Results Processed')
        REVIEW_STARTED = 'REVIEW_STARTED', _('Review Started')
        REVIEW_COMPLETED = 'REVIEW_COMPLETED', _('Review Completed')
        COMMENT = 'COMMENT', _('Comment Added')
        ERROR = 'ERROR', _('Error Occurred')
        SYSTEM = 'SYSTEM', _('System Event')

    # Relationship to session
    session = models.ForeignKey(
        'SearchSession',
        on_delete=models.CASCADE,
        related_name='activities',
        help_text=_('The search session this activity belongs to')
    )
    
    # Activity details
    activity_type = models.CharField(
        max_length=20,
        choices=ActivityType.choices,
        help_text=_('Type of activity recorded')
    )
    description = models.TextField(
        help_text=_('Detailed description of the activity')
    )
    
    # Status change tracking (for STATUS_CHANGED activities)
    old_status = models.CharField(
        max_length=20,
        choices=SearchSession.Status.choices,
        null=True,
        blank=True,
        help_text=_('Previous status (for status changes)')
    )
    new_status = models.CharField(
        max_length=20,
        choices=SearchSession.Status.choices,
        null=True,
        blank=True,
        help_text=_('New status (for status changes)')
    )
    
    # User who performed the activity
    performed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='session_activities',
        help_text=_('User who performed this activity')
    )
    performed_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this activity occurred')
    )
    
    # Optional structured metadata
    metadata = models.JSONField(
        null=True,
        blank=True,
        help_text=_('Additional structured data about the activity')
    )
    
    class Meta:
        ordering = ['-performed_at']
        verbose_name = _('Session Activity')
        verbose_name_plural = _('Session Activities')
        indexes = [
            models.Index(fields=['session', 'performed_at']),
            models.Index(fields=['activity_type', 'performed_at']),
            models.Index(fields=['performed_by', 'performed_at']),
        ]
        
    def __str__(self):
        return f"{self.get_activity_type_display()} on {self.session.title} at {self.performed_at}"
    
    @classmethod
    def log_activity(cls, session, activity_type, description, user, **kwargs):
        """
        Convenience method to log an activity.
        
        Args:
            session: SearchSession instance
            activity_type: ActivityType choice
            description: Human-readable description
            user: User who performed the action
            **kwargs: Additional fields (old_status, new_status, metadata)
        """
        return cls.objects.create(
            session=session,
            activity_type=activity_type,
            description=description,
            performed_by=user,
            **kwargs
        )


# Import timezone for stats calculation
from django.utils import timezone
