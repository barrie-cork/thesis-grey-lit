from django import template
from django.utils import timezone
from datetime import timedelta

register = template.Library()

@register.filter
def duration_display(value):
    """
    Convert a timedelta object to a human-readable duration string.
    
    Args:
        value: datetime.timedelta object
    
    Returns:
        str: Human-readable duration (e.g., "2 days, 3 hours")
    """
    if not isinstance(value, timedelta):
        return str(value)
    
    if value.total_seconds() < 0:
        return "0 seconds"
    
    days = value.days
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    parts = []
    
    if days > 0:
        parts.append(f"{days} day{'s' if days != 1 else ''}")
    
    if hours > 0:
        parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
    
    if minutes > 0 and days == 0:  # Only show minutes if no days
        parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
    
    if not parts:  # Less than a minute
        parts.append("Less than a minute")
    
    if len(parts) > 2:
        # Join first parts with commas and last with 'and'
        return f"{', '.join(parts[:-1])}, and {parts[-1]}"
    elif len(parts) == 2:
        return f"{parts[0]} and {parts[1]}"
    else:
        return parts[0]

@register.filter
def duration_short(value):
    """
    Convert a timedelta object to a short duration string.
    
    Args:
        value: datetime.timedelta object
    
    Returns:
        str: Short duration (e.g., "2d 3h", "45m", "12s")
    """
    if not isinstance(value, timedelta):
        return str(value)
    
    if value.total_seconds() < 0:
        return "0s"
    
    days = value.days
    hours, remainder = divmod(value.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if days > 0:
        if hours > 0:
            return f"{days}d {hours}h"
        return f"{days}d"
    elif hours > 0:
        if minutes > 0:
            return f"{hours}h {minutes}m"
        return f"{hours}h"
    elif minutes > 0:
        return f"{minutes}m"
    else:
        return f"{seconds}s"

@register.filter
def percentage(value, total):
    """
    Calculate percentage of value relative to total.
    
    Args:
        value: Numeric value
        total: Total value for percentage calculation
    
    Returns:
        str: Percentage with one decimal place
    """
    try:
        if total == 0:
            return "0.0%"
        return f"{(value / total * 100):.1f}%"
    except (TypeError, ZeroDivisionError):
        return "0.0%"

@register.filter
def status_class(status):
    """
    Convert status to CSS class name.
    
    Args:
        status: Status string
    
    Returns:
        str: CSS class name
    """
    return f"status-{status.lower().replace(' ', '_')}"

@register.filter
def activity_icon(activity_type):
    """
    Get appropriate icon for activity type.
    
    Args:
        activity_type: Activity type string
    
    Returns:
        str: Icon class name
    """
    icon_map = {
        'CREATED': 'fa-plus-circle',
        'STATUS_CHANGED': 'fa-exchange-alt',
        'MODIFIED': 'fa-edit',
        'STRATEGY_DEFINED': 'fa-strategy',
        'SEARCH_EXECUTED': 'fa-search',
        'RESULTS_PROCESSED': 'fa-cogs',
        'REVIEW_STARTED': 'fa-play',
        'REVIEW_COMPLETED': 'fa-check-circle',
        'COMMENT': 'fa-comment',
        'ERROR': 'fa-exclamation-triangle',
        'SYSTEM': 'fa-robot',
    }
    return icon_map.get(activity_type, 'fa-circle')

@register.simple_tag
def transition_arrow(from_status, to_status):
    """
    Generate appropriate arrow for status transition.
    
    Args:
        from_status: Previous status
        to_status: New status
    
    Returns:
        str: HTML for transition arrow
    """
    status_order = [
        'draft', 'strategy_ready', 'executing', 'processing',
        'ready_for_review', 'in_review', 'completed', 'archived'
    ]
    
    if not from_status:
        return '<i class="fa fa-plus text-success"></i>'
    
    if to_status == 'failed':
        return '<i class="fa fa-times text-danger"></i>'
    
    try:
        from_index = status_order.index(from_status)
        to_index = status_order.index(to_status)
        
        if to_index > from_index:
            return '<i class="fa fa-arrow-up text-success"></i>'
        elif to_index < from_index:
            return '<i class="fa fa-arrow-down text-warning"></i>'
        else:
            return '<i class="fa fa-arrow-right text-info"></i>'
    except ValueError:
        return '<i class="fa fa-arrow-right text-secondary"></i>'

@register.filter
def get_item(dictionary, key):
    """
    Get item from dictionary by key.
    
    Args:
        dictionary: Dictionary object
        key: Key to look up
    
    Returns:
        Any: Value from dictionary or empty string
    """
    if isinstance(dictionary, dict):
        return dictionary.get(key, '')
    return ''

@register.filter
def multiply(value, multiplier):
    """
    Multiply two values.
    
    Args:
        value: First value
        multiplier: Second value
    
    Returns:
        Numeric: Product of the two values
    """
    try:
        return float(value) * float(multiplier)
    except (ValueError, TypeError):
        return 0

@register.filter
def format_number(value):
    """
    Format number with appropriate separators.
    
    Args:
        value: Numeric value
    
    Returns:
        str: Formatted number
    """
    try:
        if isinstance(value, float):
            if value.is_integer():
                return f"{int(value):,}"
            else:
                return f"{value:,.1f}"
        else:
            return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)
