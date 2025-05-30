import uuid
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

    # Use UUID primary key to align with custom User model
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_('Unique identifier for the search session')
    )

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
        # Sprint 7 recovery activities
        ERROR_RECOVERY = 'error_recovery', _('Error Recovery')
        RECOVERY_ATTEMPT = 'recovery_attempt', _('Recovery Attempt')
        FAILED = 'failed', _('Failed')

    # Use UUID primary key for consistency
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_('Unique identifier for this activity')
    )

    # Relationship to session
    session = models.ForeignKey(
        'SearchSession',
        on_delete=models.CASCADE,
        related_name='activities',
        help_text=_('The search session this activity belongs to')
    )
    
    # Activity details - using 'action' for backward compatibility with tests
    action = models.CharField(
        max_length=50,
        help_text=_('Type of activity recorded')
    )
    description = models.TextField(
        blank=True,
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
    
    # User who performed the activity - using 'user' for backward compatibility
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='session_activities',
        help_text=_('User who performed this activity')
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this activity occurred')
    )
    
    # Optional structured metadata - using 'details' for backward compatibility
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional structured data about the activity')
    )
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = _('Session Activity')
        verbose_name_plural = _('Session Activities')
        indexes = [
            models.Index(fields=['session', 'timestamp']),
            models.Index(fields=['action', 'timestamp']),
            models.Index(fields=['user', 'timestamp']),
        ]
        
    def __str__(self):
        # Get the display value for the action
        action_display = dict(self.ActivityType.choices).get(self.action, self.action)
        return f"{action_display} on {self.session.title} at {self.timestamp}"
    
    @classmethod
    def log_activity(cls, session, action, description, user, **kwargs):
        """
        Convenience method to log an activity.
        
        Args:
            session: SearchSession instance
            action: Action type string
            description: Human-readable description
            user: User who performed the action
            **kwargs: Additional fields (old_status, new_status, details)
        """
        return cls.objects.create(
            session=session,
            action=action,
            description=description,
            user=user,
            **kwargs
        )


# Import timezone for stats calculation
from django.utils import timezone


class SessionStatusHistory(models.Model):
    """
    Track detailed history of all status changes for audit purposes.
    Sprint 6: Advanced status change tracking with full audit trail.
    """
    
    # Use UUID primary key for consistency
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_('Unique identifier for this status history record')
    )
    
    session = models.ForeignKey(
        'SearchSession',
        on_delete=models.CASCADE,
        related_name='status_history',
        help_text=_('The session this status change belongs to')
    )
    
    # Status transition details
    from_status = models.CharField(
        max_length=20,
        choices=SearchSession.Status.choices,
        blank=True,
        help_text=_('Previous status (empty for initial creation)')
    )
    to_status = models.CharField(
        max_length=20,
        choices=SearchSession.Status.choices,
        help_text=_('New status after change')
    )
    
    # Change attribution and timing
    changed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='status_changes',
        help_text=_('User who initiated this status change')
    )
    changed_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('Exact time of status change')
    )
    
    # Optional reason and context
    reason = models.TextField(
        blank=True,
        help_text=_('Optional reason for the status change')
    )
    
    # Structured metadata for additional context
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Additional context about the status change')
    )
    
    # IP address for security auditing
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text=_('IP address from which change was made')
    )
    
    # Duration in previous status (calculated field)
    duration_in_previous_status = models.DurationField(
        null=True,
        blank=True,
        help_text=_('How long the session was in the previous status')
    )
    
    class Meta:
        ordering = ['-changed_at']
        verbose_name = _('Session Status History')
        verbose_name_plural = _('Session Status Histories')
        indexes = [
            models.Index(fields=['session', '-changed_at']),
            models.Index(fields=['changed_by', '-changed_at']),
            models.Index(fields=['from_status', 'to_status']),
            models.Index(fields=['-changed_at']),
        ]
        
    def __str__(self):
        if self.from_status:
            return f"{self.session.title}: {self.from_status} → {self.to_status}"
        else:
            return f"{self.session.title}: Created with status {self.to_status}"
    
    def get_transition_display(self):
        """Get human-readable transition description"""
        if self.from_status:
            from_display = dict(SearchSession.Status.choices).get(self.from_status, self.from_status)
            to_display = dict(SearchSession.Status.choices).get(self.to_status, self.to_status)
            return f"{from_display} → {to_display}"
        else:
            to_display = dict(SearchSession.Status.choices).get(self.to_status, self.to_status)
            return f"Created as {to_display}"
    
    @property
    def is_progression(self):
        """Determine if this change represents forward progress"""
        status_order = [
            'draft', 'strategy_ready', 'executing', 'processing',
            'ready_for_review', 'in_review', 'completed', 'archived'
        ]
        
        if not self.from_status:
            return True  # Initial creation is always progression
        
        try:
            from_index = status_order.index(self.from_status)
            to_index = status_order.index(self.to_status)
            return to_index > from_index
        except ValueError:
            # Handle failed status or other edge cases
            return self.to_status != 'failed'
    
    @property
    def is_regression(self):
        """Determine if this change represents backward movement"""
        if not self.from_status:
            return False
        return not self.is_progression and self.to_status != 'failed'
    
    @property
    def is_error_recovery(self):
        """Determine if this change represents recovery from error"""
        return self.from_status == 'failed' and self.to_status != 'failed'


class SessionArchive(models.Model):
    """
    Track archiving operations for completed sessions.
    Sprint 6: Comprehensive archiving system with metadata.
    """
    
    # Use UUID primary key for consistency
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_('Unique identifier for this archive record')
    )
    
    session = models.OneToOneField(
        'SearchSession',
        on_delete=models.CASCADE,
        related_name='archive_info',
        help_text=_('The archived session')
    )
    
    # Archive operation details
    archived_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='archived_sessions',
        help_text=_('User who archived this session')
    )
    archived_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this session was archived')
    )
    
    # Archive metadata
    archive_reason = models.TextField(
        blank=True,
        help_text=_('Optional reason for archiving')
    )
    
    # Archive statistics snapshot
    stats_snapshot = models.JSONField(
        default=dict,
        help_text=_('Session statistics at time of archiving')
    )
    
    # Restore tracking
    restored_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('When this session was last restored from archive')
    )
    restored_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='restored_sessions',
        help_text=_('User who last restored this session')
    )
    
    class Meta:
        ordering = ['-archived_at']
        verbose_name = _('Session Archive')
        verbose_name_plural = _('Session Archives')
        indexes = [
            models.Index(fields=['archived_by', '-archived_at']),
            models.Index(fields=['-archived_at']),
        ]
        
    def __str__(self):
        return f"Archive: {self.session.title} (archived {self.archived_at.date()})"
    
    @property
    def is_currently_archived(self):
        """Check if session is currently in archived state"""
        return self.session.status == SearchSession.Status.ARCHIVED
    
    @property
    def days_archived(self):
        """Calculate how many days session has been archived"""
        if self.restored_at:
            return (self.restored_at - self.archived_at).days
        return (timezone.now() - self.archived_at).days


class UserSessionStats(models.Model):
    """
    Track user-level statistics and productivity metrics.
    Sprint 6: Advanced analytics and insights dashboard.
    """
    
    # Use UUID primary key for consistency
    id = models.UUIDField(
        primary_key=True, 
        default=uuid.uuid4, 
        editable=False,
        help_text=_('Unique identifier for this stats record')
    )
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='session_stats',
        help_text=_('User these statistics belong to')
    )
    
    # Session counts by status
    total_sessions = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of sessions created')
    )
    completed_sessions = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of sessions completed')
    )
    archived_sessions = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of sessions archived')
    )
    failed_sessions = models.PositiveIntegerField(
        default=0,
        help_text=_('Number of sessions that failed')
    )
    
    # Productivity metrics
    avg_completion_time = models.DurationField(
        null=True,
        blank=True,
        help_text=_('Average time to complete a session')
    )
    fastest_completion = models.DurationField(
        null=True,
        blank=True,
        help_text=_('Fastest session completion time')
    )
    
    # Activity metrics
    total_activities = models.PositiveIntegerField(
        default=0,
        help_text=_('Total number of activities performed')
    )
    last_activity_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_('Date of last session activity')
    )
    
    # Usage patterns
    most_active_day = models.CharField(
        max_length=10,
        blank=True,
        help_text=_('Day of week user is most active')
    )
    most_active_hour = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text=_('Hour of day user is most active')
    )
    
    # Calculated fields
    completion_rate = models.FloatField(
        default=0.0,
        help_text=_('Percentage of sessions completed')
    )
    productivity_score = models.FloatField(
        default=0.0,
        help_text=_('Overall productivity score (0-100)')
    )
    
    # Metadata and caching
    stats_calculated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When these statistics were last calculated')
    )
    calculation_metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Metadata about statistics calculation')
    )
    
    # Sprint 7: Notification preferences
    notification_preferences = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('User notification preferences for real-time updates')
    )
    
    class Meta:
        verbose_name = _('User Session Statistics')
        verbose_name_plural = _('User Session Statistics')
        
    def __str__(self):
        return f"Stats for {self.user.username}: {self.completed_sessions}/{self.total_sessions} completed"
    
    def calculate_completion_rate(self):
        """Calculate and update completion rate"""
        if self.total_sessions > 0:
            self.completion_rate = (self.completed_sessions / self.total_sessions) * 100
        else:
            self.completion_rate = 0.0
        return self.completion_rate
    
    def calculate_productivity_score(self):
        """Calculate overall productivity score"""
        score = 0.0
        
        # Completion rate contributes 40%
        score += self.completion_rate * 0.4
        
        # Low failure rate contributes 30%
        if self.total_sessions > 0:
            failure_rate = (self.failed_sessions / self.total_sessions) * 100
            score += max(0, 100 - failure_rate) * 0.3
        
        # Regular activity contributes 30%
        if self.last_activity_date:
            days_since_activity = (timezone.now() - self.last_activity_date).days
            activity_score = max(0, 100 - (days_since_activity * 2))  # Decay over time
            score += activity_score * 0.3
        
        self.productivity_score = min(100.0, score)
        return self.productivity_score
    
    @classmethod
    def update_user_stats(cls, user):
        """Update or create statistics for a user"""
        stats, created = cls.objects.get_or_create(user=user)
        
        # Get user's sessions
        sessions = user.created_sessions.all()
        
        # Calculate basic counts
        stats.total_sessions = sessions.count()
        stats.completed_sessions = sessions.filter(status='completed').count()
        stats.archived_sessions = sessions.filter(status='archived').count()
        stats.failed_sessions = sessions.filter(status='failed').count()
        
        # Calculate timing metrics
        completed_sessions = sessions.filter(
            status__in=['completed', 'archived'],
            completed_date__isnull=False
        )
        
        if completed_sessions.exists():
            completion_times = []
            for session in completed_sessions:
                if session.start_date:
                    duration = session.completed_date - session.start_date
                    completion_times.append(duration)
            
            if completion_times:
                stats.avg_completion_time = sum(completion_times, timezone.timedelta()) / len(completion_times)
                stats.fastest_completion = min(completion_times)
        
        # Activity metrics
        activities = user.session_activities.all()
        stats.total_activities = activities.count()
        if activities.exists():
            stats.last_activity_date = activities.first().timestamp
        
        # Calculate derived metrics
        stats.calculate_completion_rate()
        stats.calculate_productivity_score()
        
        stats.save()
        return stats
