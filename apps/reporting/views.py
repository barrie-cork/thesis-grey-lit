from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.review_manager.models import SearchSession

@login_required
def summary(request, session_id):
    session = get_object_or_404(SearchSession, id=session_id, created_by=request.user)
    
    context = {
        'session': session,
        'app_name': 'Reporting',
        'feature_description': 'Generate comprehensive review reports',
        'expected_features': [
            'PRISMA flow diagrams',
            'Search strategy documentation',
            'Results summary tables',
            'Export to multiple formats',
            'Citation management',
            'Review quality metrics'
        ]
    }
    return render(request, 'placeholder_app.html', context)
