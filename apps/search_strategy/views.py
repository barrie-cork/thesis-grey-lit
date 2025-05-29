from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.review_manager.models import SearchSession

@login_required
def define_strategy_view(request, session_id):
    """Minimal implementation for search strategy definition"""
    session = get_object_or_404(SearchSession, id=session_id, created_by=request.user)
    return render(request, 'search_strategy/define.html', {'session': session})
