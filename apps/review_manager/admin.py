from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import SearchSession, SessionActivity

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
    list_display = ('session', 'activity_type', 'performed_by', 'performed_at')
    list_filter = ('activity_type', 'performed_at', 'session__status')
    search_fields = ('session__title', 'description', 'performed_by__username')
    readonly_fields = ('performed_at',)
    
    fieldsets = (
        (None, {
            'fields': ('session', 'activity_type', 'description')
        }),
        (_('Status Change'), {
            'fields': ('old_status', 'new_status'),
            'classes': ('collapse',),
            'description': _('Only applicable for status change activities')
        }),
        (_('Additional Data'), {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        (_('Metadata'), {
            'fields': ('performed_by', 'performed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # If creating new object
            obj.performed_by = request.user
        super().save_model(request, obj, form, change)
