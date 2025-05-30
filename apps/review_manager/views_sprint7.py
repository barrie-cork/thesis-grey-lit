# apps/review_manager/views_sprint7.py

"""
Sprint 7: Polish & Performance Views
Real-time status indicators, AJAX notifications, error recovery, and auto-dismiss functionality
"""

import json
import time
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.core.cache import cache
from django.db.models import Q, Count, Prefetch

from .models import SearchSession, SessionActivity, UserSessionStats
from .recovery import ErrorRecoveryManager

User = get_user_model()


@require_http_methods(["POST"])
@login_required
@csrf_protect
def status_check_api(request):
    """
    API endpoint for real-time status checking
    
    Accepts POST data:
    {
        "session_ids": [1, 2, 3, ...]
    }
    
    Returns:
    {
        "success": true,
        "sessions": {
            "1": {
                "status": "executing",
                "status_display": "Executing Searches",
                "updated_at": "2025-05-30T10:30:00Z",
                "progress": 65,
                "estimated_completion": "2025-05-30T10:45:00Z"
            }
        },
        "timestamp": "2025-05-30T10:30:15Z"
    }
    """
    try:
        data = json.loads(request.body)
        session_ids = data.get('session_ids', [])
        
        if not session_ids:
            return JsonResponse({
                'success': False,
                'error': 'No session IDs provided'
            }, status=400)
        
        # Limit to reasonable number to prevent abuse
        if len(session_ids) > 100:
            return JsonResponse({
                'success': False,
                'error': 'Too many session IDs (max 100)'
            }, status=400)
        
        # Get sessions with optimized query
        sessions = SearchSession.objects.filter(
            id__in=session_ids,
            created_by=request.user
        ).select_related('created_by').values(
            'id', 'status', 'updated_at', 'title'
        )
        
        # Build session data with progress information
        session_data = {}
        for session in sessions:
            session_id = session['id']
            status = session['status']
            
            # Get progress and completion estimates
            progress_info = get_session_progress(session_id, status)
            
            session_data[str(session_id)] = {
                'status': status,
                'status_display': dict(SearchSession.Status.choices)[status],
                'updated_at': session['updated_at'].isoformat(),
                'title': session['title'],
                **progress_info
            }
        
        return JsonResponse({
            'success': True,
            'sessions': session_data,
            'timestamp': timezone.now().isoformat(),
            'poll_interval': get_optimal_poll_interval(request.user)
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


def get_session_progress(session_id, status):
    """
    Calculate progress percentage and estimates for active sessions
    
    Returns:
    {
        "progress": 65,  # percentage (0-100) or None
        "estimated_completion": "2025-05-30T10:45:00Z",  # or None
        "progress_message": "Processing 650 of 1000 results"
    }
    """
    progress_info = {
        'progress': None,
        'estimated_completion': None,
        'progress_message': None
    }
    
    if status == 'executing':
        # Check search execution progress
        try:
            # This would normally import from serp_execution app
            # For now, simulate progress
            cache_key = f'execution_progress_{session_id}'
            cached_progress = cache.get(cache_key)
            
            if cached_progress is not None:
                progress_info['progress'] = cached_progress
                progress_info['progress_message'] = f"Executing searches: {cached_progress}% complete"
                
                # Estimate completion (simplified calculation)
                if cached_progress > 0 and cached_progress < 100:
                    remaining_time = (100 - cached_progress) * 2  # 2 minutes per 1%
                    estimated_completion = timezone.now() + timezone.timedelta(minutes=remaining_time)
                    progress_info['estimated_completion'] = estimated_completion.isoformat()
            
        except Exception:
            # Fallback to no progress info
            pass
    
    elif status == 'processing':
        # Check result processing progress
        try:
            # This would normally import from results_manager app
            # For now, simulate progress
            cache_key = f'processing_progress_{session_id}'
            cached_progress = cache.get(cache_key)
            
            if cached_progress is not None:
                progress_info['progress'] = cached_progress
                progress_info['progress_message'] = f"Processing results: {cached_progress}% complete"
                
                if cached_progress > 0 and cached_progress < 100:
                    remaining_time = (100 - cached_progress) * 0.5  # 30 seconds per 1%
                    estimated_completion = timezone.now() + timezone.timedelta(seconds=remaining_time * 30)
                    progress_info['estimated_completion'] = estimated_completion.isoformat()
            
        except Exception:
            pass
    
    return progress_info


def get_optimal_poll_interval(user):
    """
    Calculate optimal polling interval based on user activity and system load
    Returns interval in milliseconds
    """
    # Base interval: 5 seconds
    base_interval = 5000
    
    # Check if user has active sessions
    active_sessions = SearchSession.objects.filter(
        created_by=user,
        status__in=['executing', 'processing']
    ).count()
    
    if active_sessions == 0:
        # No active sessions, poll less frequently
        return base_interval * 3  # 15 seconds
    elif active_sessions > 5:
        # Many active sessions, poll more frequently
        return base_interval // 2  # 2.5 seconds
    else:
        return base_interval


@require_http_methods(["POST"])
@login_required
@csrf_protect
def notification_preferences_api(request):
    """
    Manage user notification preferences
    
    Accepts POST data:
    {
        "preferences": {
            "auto_dismiss_duration": 5000,
            "show_status_changes": true,
            "show_error_notifications": true,
            "show_success_notifications": true,
            "notification_position": "top-right",
            "sound_enabled": false
        }
    }
    """
    try:
        data = json.loads(request.body)
        preferences = data.get('preferences', {})
        
        # Get or create user notification preferences
        user_stats, created = UserSessionStats.objects.get_or_create(
            user=request.user,
            defaults={
                'notification_preferences': {}
            }
        )
        
        # Update preferences
        current_prefs = user_stats.notification_preferences or {}
        
        # Validate and update preferences
        valid_prefs = {
            'auto_dismiss_duration': min(max(int(preferences.get('auto_dismiss_duration', 5000)), 1000), 30000),
            'show_status_changes': bool(preferences.get('show_status_changes', True)),
            'show_error_notifications': bool(preferences.get('show_error_notifications', True)),
            'show_success_notifications': bool(preferences.get('show_success_notifications', True)),
            'notification_position': preferences.get('notification_position', 'top-right'),
            'sound_enabled': bool(preferences.get('sound_enabled', False))
        }
        
        # Validate position
        valid_positions = ['top-left', 'top-right', 'bottom-left', 'bottom-right']
        if valid_prefs['notification_position'] not in valid_positions:
            valid_prefs['notification_position'] = 'top-right'
        
        current_prefs.update(valid_prefs)
        user_stats.notification_preferences = current_prefs
        user_stats.save()
        
        return JsonResponse({
            'success': True,
            'preferences': current_prefs
        })
        
    except (json.JSONDecodeError, ValueError) as e:
        return JsonResponse({
            'success': False,
            'error': f'Invalid data: {str(e)}'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def notification_preferences_get(request):
    """Get current user notification preferences"""
    try:
        user_stats, created = UserSessionStats.objects.get_or_create(
            user=request.user,
            defaults={
                'notification_preferences': {}
            }
        )
        
        # Default preferences
        default_prefs = {
            'auto_dismiss_duration': 5000,
            'show_status_changes': True,
            'show_error_notifications': True,
            'show_success_notifications': True,
            'notification_position': 'top-right',
            'sound_enabled': False
        }
        
        preferences = user_stats.notification_preferences or {}
        
        # Merge with defaults
        for key, default_value in default_prefs.items():
            if key not in preferences:
                preferences[key] = default_value
        
        return JsonResponse({
            'success': True,
            'preferences': preferences
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@csrf_protect
def error_recovery_api(request):
    """
    Handle error recovery actions
    
    Accepts POST data:
    {
        "session_id": 123,
        "error_type": "search_execution_failed",
        "action": "retry_execution"
    }
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        error_type = data.get('error_type')
        action = data.get('action')
        
        if not all([session_id, error_type, action]):
            return JsonResponse({
                'success': False,
                'error': 'Missing required parameters'
            }, status=400)
        
        # Get session and verify ownership
        session = get_object_or_404(
            SearchSession,
            id=session_id,
            created_by=request.user
        )
        
        # Handle recovery action
        recovery_result = handle_recovery_action(session, error_type, action, request.user)
        
        if recovery_result['success']:
            # Log recovery action
            SessionActivity.objects.create(
                session=session,
                action='error_recovery',
                user=request.user,
                details={
                    'error_type': error_type,
                    'recovery_action': action,
                    'result': recovery_result.get('message', 'Recovery action completed')
                }
            )
        
        return JsonResponse(recovery_result)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


def handle_recovery_action(session, error_type, action, user):
    """
    Execute a specific recovery action
    
    Returns:
    {
        "success": True,
        "message": "Recovery action completed successfully",
        "next_action": "wait_for_completion",  # optional
        "redirect_url": "/path/to/page"  # optional
    }
    """
    try:
        if error_type == 'search_execution_failed':
            if action == 'retry_execution':
                # Reset session status to allow retry
                session.status = 'strategy_ready'
                session.save()
                
                return {
                    'success': True,
                    'message': 'Session has been reset. You can now retry search execution.',
                    'redirect_url': f'/review/session/{session.id}/'
                }
            
            elif action == 'edit_strategy':
                return {
                    'success': True,
                    'message': 'Redirecting to strategy editor.',
                    'redirect_url': f'/strategy/define/{session.id}/'
                }
            
            elif action == 'contact_support':
                return {
                    'success': True,
                    'message': 'Support contact information will be displayed.',
                    'show_support_modal': True
                }
        
        elif error_type == 'processing_timeout':
            if action == 'resume_processing':
                # Mark session for processing resume
                session.status = 'processing'
                session.save()
                
                return {
                    'success': True,
                    'message': 'Processing will resume shortly.',
                    'next_action': 'wait_for_completion'
                }
            
            elif action == 'batch_processing':
                # Enable batch processing mode
                session.status = 'processing'
                session.save()
                
                # Store batch processing preference
                session.permissions = session.permissions or {}
                session.permissions['batch_processing'] = True
                session.save()
                
                return {
                    'success': True,
                    'message': 'Batch processing mode enabled. Processing will resume in smaller chunks.',
                    'next_action': 'wait_for_completion'
                }
        
        # Default fallback
        return {
            'success': False,
            'error': f'Unknown recovery action: {action} for error type: {error_type}'
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': f'Recovery action failed: {str(e)}'
        }


@require_http_methods(["GET"])
@login_required
def get_error_recovery_options(request, session_id):
    """
    Get available recovery options for a session in error state
    """
    try:
        session = get_object_or_404(
            SearchSession,
            id=session_id,
            created_by=request.user
        )
        
        if session.status != 'failed':
            return JsonResponse({
                'success': False,
                'error': 'Session is not in failed state'
            }, status=400)
        
        # Get the last error from activity log
        last_error_activity = SessionActivity.objects.filter(
            session=session,
            action__in=['error', 'failed', 'timeout']
        ).order_by('-timestamp').first()
        
        if last_error_activity:
            error_type = last_error_activity.details.get('error_type', 'unknown_error')
        else:
            error_type = 'unknown_error'
        
        # Get recovery options
        recovery_options = ErrorRecoveryManager.get_recovery_options(error_type, session)
        
        return JsonResponse({
            'success': True,
            'recovery_options': recovery_options,
            'session_status': session.status,
            'error_details': last_error_activity.details if last_error_activity else None
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
@login_required
@csrf_protect
def simulate_progress_update(request):
    """
    Development endpoint to simulate progress updates
    This would normally be handled by the actual execution/processing systems
    """
    try:
        data = json.loads(request.body)
        session_id = data.get('session_id')
        progress_type = data.get('type', 'execution')  # 'execution' or 'processing'
        progress_value = min(max(int(data.get('progress', 0)), 0), 100)
        
        # Store in cache (in production, this would be handled by the actual systems)
        cache_key = f'{progress_type}_progress_{session_id}'
        cache.set(cache_key, progress_value, timeout=300)  # 5 minutes
        
        return JsonResponse({
            'success': True,
            'message': f'Progress updated to {progress_value}%',
            'progress': progress_value
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
@login_required
def system_health_check(request):
    """
    System health check for real-time monitoring
    Returns system status and performance metrics
    """
    try:
        # Check database connectivity
        db_check_start = time.time()
        session_count = SearchSession.objects.filter(created_by=request.user).count()
        db_check_time = (time.time() - db_check_start) * 1000  # ms
        
        # Check cache connectivity
        cache_check_start = time.time()
        cache.set('health_check', 'ok', timeout=10)
        cache_value = cache.get('health_check')
        cache_check_time = (time.time() - cache_check_start) * 1000  # ms
        
        # System metrics
        health_data = {
            'status': 'healthy',
            'timestamp': timezone.now().isoformat(),
            'checks': {
                'database': {
                    'status': 'ok' if session_count >= 0 else 'error',
                    'response_time_ms': round(db_check_time, 2),
                    'user_sessions': session_count
                },
                'cache': {
                    'status': 'ok' if cache_value == 'ok' else 'error',
                    'response_time_ms': round(cache_check_time, 2)
                }
            },
            'performance': {
                'avg_db_response_ms': round(db_check_time, 2),
                'avg_cache_response_ms': round(cache_check_time, 2),
                'recommended_poll_interval_ms': get_optimal_poll_interval(request.user)
            }
        }
        
        # Determine overall health
        if db_check_time > 1000 or cache_check_time > 100:
            health_data['status'] = 'degraded'
        
        if cache_value != 'ok':
            health_data['status'] = 'warning'
        
        return JsonResponse({
            'success': True,
            'health': health_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': f'Health check failed: {str(e)}',
            'health': {
                'status': 'error',
                'timestamp': timezone.now().isoformat()
            }
        }, status=500)
