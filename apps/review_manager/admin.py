from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import (
    SearchSession, SessionActivity, SessionStatusHistory, 
    SessionArchive, UserSessionStats
)

@admin.register(SearchSession)
class SearchSessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_by', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('title', 'description', 'created_by__username')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        (None, {
            'fields': ('title', 'description')
        }),
        (_('Status'), {
            'fields': ('status',)
        }),
        (_('Dates'), {
            'fields': ('start_date', 'completed_date')
        }),
        (_('Metadata'), {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

@admin.register(SessionActivity)
class SessionActivityAdmin(admin.ModelAdmin):
    list_display = ('session', 'action', 'user', 'timestamp')
    list_filter = ('action', 'timestamp', 'session__status')
    search_fields = ('session__title', 'description', 'user__username')
    readonly_fields = ('timestamp',)
    
    fieldsets = (
        (None, {
            'fields': ('session', 'action', 'description')
        }),
        (_('Status Change'), {
            'fields': ('old_status', 'new_status'),
            'classes': ('collapse',),
            'description': _('Only applicable for status change activities')
        }),
        (_('Additional Data'), {
            'fields': ('details',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('user', 'timestamp'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.user = request.user
        super().save_model(request, obj, form, change)


# Sprint 6: New Model Admin Classes

@admin.register(SessionStatusHistory)
class SessionStatusHistoryAdmin(admin.ModelAdmin):
    """
    Sprint 6 Task 32: Admin interface for status history tracking.
    """
    list_display = (
        'session', 'from_status', 'to_status', 'changed_by', 
        'changed_at', 'is_progression', 'is_regression'
    )
    list_filter = (
        'to_status', 'from_status', 'changed_at', 
        'session__status', 'changed_by'
    )
    search_fields = (
        'session__title', 'reason', 'changed_by__username'
    )
    readonly_fields = (
        'changed_at', 'duration_in_previous_status', 
        'is_progression', 'is_regression', 'is_error_recovery'
    )
    
    fieldsets = (
        (None, {
            'fields': ('session', 'from_status', 'to_status')
        }),
        (_('Change Details'), {
            'fields': ('changed_by', 'changed_at', 'reason')
        }),
        (_('Timing Analysis'), {
            'fields': ('duration_in_previous_status',),
            'classes': ('collapse',)
        }),
        (_('Transition Analysis'), {
            'fields': ('is_progression', 'is_regression', 'is_error_recovery'),
            'classes': ('collapse',)
        }),
        (_('Additional Context'), {
            'fields': ('metadata', 'ip_address'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'changed_at'
    ordering = ['-changed_at']


@admin.register(SessionArchive)
class SessionArchiveAdmin(admin.ModelAdmin):
    """
    Sprint 6 Task 33: Admin interface for archive management.
    """
    list_display = (
        'session', 'archived_by', 'archived_at', 
        'restored_at', 'is_currently_archived', 'days_archived'
    )
    list_filter = (
        'archived_at', 'restored_at', 'archived_by'
    )
    search_fields = (
        'session__title', 'archive_reason', 'archived_by__username'
    )
    readonly_fields = (
        'archived_at', 'restored_at', 'is_currently_archived', 
        'days_archived', 'stats_snapshot'
    )
    
    fieldsets = (
        (None, {
            'fields': ('session', 'archive_reason')
        }),
        (_('Archive Details'), {
            'fields': ('archived_by', 'archived_at')
        }),
        (_('Restore Details'), {
            'fields': ('restored_by', 'restored_at'),
            'classes': ('collapse',)
        }),
        (_('Statistics Snapshot'), {
            'fields': ('stats_snapshot',),
            'classes': ('collapse',)
        }),
        (_('Calculated Fields'), {
            'fields': ('is_currently_archived', 'days_archived'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'archived_at'
    ordering = ['-archived_at']


@admin.register(UserSessionStats)
class UserSessionStatsAdmin(admin.ModelAdmin):
    """
    Sprint 6 Task 35: Admin interface for user statistics.
    """
    list_display = (
        'user', 'total_sessions', 'completed_sessions', 
        'completion_rate', 'productivity_score', 'stats_calculated_at'
    )
    list_filter = (
        'stats_calculated_at', 'most_active_day', 
        'completion_rate', 'productivity_score'
    )
    search_fields = ('user__username', 'user__email')
    readonly_fields = (
        'stats_calculated_at', 'completion_rate', 'productivity_score'
    )
    
    fieldsets = (
        (None, {
            'fields': ('user',)
        }),
        (_('Session Statistics'), {
            'fields': (
                'total_sessions', 'completed_sessions', 
                'archived_sessions', 'failed_sessions'
            )
        }),
        (_('Productivity Metrics'), {
            'fields': (
                'avg_completion_time', 'fastest_completion',
                'completion_rate', 'productivity_score'
            )
        }),
        (_('Activity Metrics'), {
            'fields': (
                'total_activities', 'last_activity_date'
            ),
            'classes': ('collapse',)
        }),
        (_('Usage Patterns'), {
            'fields': (
                'most_active_day', 'most_active_hour'
            ),
            'classes': ('collapse',)
        }),
        (_('Calculation Metadata'), {
            'fields': (
                'stats_calculated_at', 'calculation_metadata'
            ),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'stats_calculated_at'
    ordering = ['-stats_calculated_at']
    
    actions = ['recalculate_stats']
    
    def recalculate_stats(self, request, queryset):
        """
        Admin action to recalculate statistics for selected users.
        """
        count = 0
        for stats in queryset:
            UserSessionStats.update_user_stats(stats.user)
            count += 1
        
        self.message_user(
            request,
            f'Successfully recalculated statistics for {count} user{"s" if count != 1 else ""}.',
        )
    
    recalculate_stats.short_description = 'Recalculate statistics for selected users'
