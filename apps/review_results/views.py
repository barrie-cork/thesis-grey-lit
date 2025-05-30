from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.review_manager.models import SearchSession

@login_required
def overview(request, session_id):
    session = get_object_or_404(SearchSession, id=session_id, created_by=request.user)
    
    context = {
        'session': session,
        'app_name': 'Results Review',
        'feature_description': 'Review and categorise search results',
        'expected_features': [
            'Results listing and filtering',
            'Include/exclude decisions',
            'Duplicate detection',
            'Export functionality',
            'Screening workflow',
            'Collaboration tools'
        ]
    }
    return render(request, 'placeholder_app.html', context)
