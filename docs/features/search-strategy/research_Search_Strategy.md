# Search Strategy Builder Implementation Plan
## Final Version - Aligned with thesis-grey-lit Architecture

### 📋 **Executive Summary**

This is a guide for building the Search Strategy Builder app within the thesis-grey-lit Django project. The app enables researchers to define systematic search strategies using the PIC framework (Population, Interest, Context) for grey literature searches.

**Key Features:**
- Chip-based term input for PIC categories
- Flexible search configuration (domains, file types, search types)
- Real-time query preview with syntax highlighting
- Direct integration with Google Search and Google Scholar
- No minimum term requirements - supports partial strategies

---

## 🎯 **Requirements Overview**

### User Experience Requirements

1. **Header Section**
   - Editable session name and description
   - Display session metadata (creation date, owner)
   - Integrated action buttons

2. **PIC Framework**
   - Three distinct panels with explanatory tooltips
   - Chip-based term management
   - Visual Boolean relationship indicators
   - No minimum term requirements per category

3. **Search Configuration**
   - Domain/URL restrictions (optional)
   - File type filters (PDF, DOC)
   - Search type selection (Web, Scholar)
   - Maximum results setting (default: 50)

4. **Query Preview**
   - Live updates with syntax highlighting
   - Copy-to-clipboard functionality
   - Direct links to search engines

### Technical Requirements

- PostgreSQL with ArrayField and JSONField
- Django 4.2/5.2 compatibility
- Integration with existing SearchSession model
- Django's built-in testing framework
- Custom User model compatibility

---

## 🏗️ **Architecture Overview**

### App Structure
```
apps/search_strategy/
├── __init__.py
├── admin.py
├── apps.py
├── forms.py
├── migrations/
├── models.py
├── signals.py
├── templates/
│   └── search_strategy/
│       └── define_strategy.html
├── tests.py
├── urls.py
├── utils.py
└── views.py
```

### Integration Points
- **Review Manager App**: Updates session status, logs activities
- **SERP Execution App**: Receives search queries for execution
- **PostgreSQL**: ArrayField for terms, JSONField for configuration

---

## 📊 **Data Models**

### SearchStrategy Model

```python
# apps/search_strategy/models.py
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from django.contrib.postgres.fields import ArrayField
from django.core.validators import MinValueValidator, MaxValueValidator
import urllib.parse

class SearchStrategy(models.Model):
    """
    Stores the search strategy for a SearchSession using PIC framework.
    Strategies can have missing terms in any PIC category.
    """
    
    # Link to SearchSession (OneToOne relationship)
    session = models.OneToOneField(
        'review_manager.SearchSession',
        on_delete=models.CASCADE,
        related_name='search_strategy',
        help_text=_('The search session this strategy belongs to')
    )
    
    # PIC Framework fields - using PostgreSQL ArrayField
    # Note: These can be empty arrays (no minimum requirement)
    population_terms = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text=_('Population terms (e.g., elderly, diabetic patients)')
    )
    
    interest_terms = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text=_('Interest/Intervention terms (e.g., insulin therapy, diet management)')
    )
    
    context_terms = ArrayField(
        models.CharField(max_length=200),
        default=list,
        blank=True,
        help_text=_('Context terms (e.g., primary care, hospital setting)')
    )
    
    # Search configuration stored as JSON
    search_config = models.JSONField(
        default=dict,
        blank=True,
        help_text=_('Search configuration including all search parameters')
    )
    # Expected structure:
    # {
    #     "domains": ["nice.org.uk", "who.int"],  # URL limiters
    #     "file_types": ["pdf", "doc"],
    #     "search_types": ["web", "scholar"],  # Which searches to run
    #     "serp_provider": "google"  # Phase 1: always google
    # }
    
    # Max results per query
    max_results = models.IntegerField(
        default=50,
        validators=[
            MinValueValidator(10),
            MaxValueValidator(500)
        ],
        help_text=_('Maximum results per search query')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Audit
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='created_strategies'
    )
    
    class Meta:
        verbose_name = _('Search Strategy')
        verbose_name_plural = _('Search Strategies')
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Strategy for: {self.session.title}"
    
    def get_term_count(self):
        """Total number of search terms across all PIC categories"""
        return (
            len(self.population_terms) + 
            len(self.interest_terms) + 
            len(self.context_terms)
        )
    
    def has_any_terms(self):
        """Check if strategy has at least one term in any category"""
        return bool(self.population_terms or self.interest_terms or self.context_terms)
    
    def generate_base_query(self):
        """Generate base Boolean search query from PIC terms"""
        query_parts = []
        
        # OR within each category
        if self.population_terms:
            pop_query = ' OR '.join(f'"{term}"' for term in self.population_terms)
            query_parts.append(f'({pop_query})')
        
        if self.interest_terms:
            int_query = ' OR '.join(f'"{term}"' for term in self.interest_terms)
            query_parts.append(f'({int_query})')
            
        if self.context_terms:
            ctx_query = ' OR '.join(f'"{term}"' for term in self.context_terms)
            query_parts.append(f'({ctx_query})')
        
        # AND between categories
        return ' AND '.join(query_parts) if query_parts else ''
    
    def generate_full_query(self, include_file_types=True, for_domain=None):
        """Generate full search query with all configurations"""
        base_query = self.generate_base_query()
        
        if not base_query:
            return ''
        
        # Add file type restrictions if requested
        if include_file_types and self.search_config.get('file_types'):
            file_type_query = ' OR '.join(f'filetype:{ft}' for ft in self.search_config['file_types'])
            base_query = f'{base_query} ({file_type_query})'
        
        # Add domain restriction if specified
        if for_domain:
            base_query = f'{base_query} site:{for_domain}'
        
        return base_query
    
    def get_google_search_url(self):
        """Generate direct Google search URL"""
        query = self.generate_base_query()
        if query:
            encoded_query = urllib.parse.quote(query)
            return f"https://www.google.com/search?q={encoded_query}"
        return None
    
    def get_scholar_search_url(self):
        """Generate Google Scholar search URL"""
        query = self.generate_base_query()
        if query:
            encoded_query = urllib.parse.quote(query)
            return f"https://scholar.google.com/scholar?q={encoded_query}"
        return None


class SearchQuery(models.Model):
    """
    Individual search queries generated from the strategy.
    Prepared for Phase 2 multi-engine support.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    strategy = models.ForeignKey(
        SearchStrategy,
        on_delete=models.CASCADE,
        related_name='queries'
    )
    
    # Query details
    query_string = models.TextField(
        help_text=_('The actual search query string')
    )
    
    search_engine = models.CharField(
        max_length=50,
        default='google',
        choices=[
            ('google', 'Google Search'),
            ('google_scholar', 'Google Scholar'),
        ]
    )
    
    # Query metadata
    query_metadata = models.JSONField(
        default=dict,
        help_text=_('Additional query parameters and metadata')
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = _('Search Query')
        verbose_name_plural = _('Search Queries')
        ordering = ['-created_at']
```

---

## 📝 **Forms Implementation**

### Core Forms

```python
# apps/search_strategy/forms.py
from django import forms
from django.core.exceptions import ValidationError
from .models import SearchStrategy

class SearchStrategyForm(forms.ModelForm):
    """Main form for search strategy configuration"""
    
    # Domain restrictions (textarea for multiple domains)
    domain_restrictions = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter domains to search, one per line (e.g., nice.org.uk)',
            'id': 'domain-restrictions'
        }),
        label='Domain/URL Restrictions',
        help_text='Leave empty to search all domains'
    )
    
    # File type filters
    file_types = forms.MultipleChoiceField(
        required=False,
        choices=[
            ('pdf', 'PDF Documents'),
            ('doc', 'Word Documents (DOC/DOCX)'),
        ],
        widget=forms.CheckboxSelectMultiple(attrs={
            'class': 'form-check-input file-type-checkbox'
        }),
        label='File Type Limitations'
    )
    
    # Search type toggles
    search_web = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'search-web'
        }),
        label='Web Search (without URL limiter)'
    )
    
    search_scholar = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'search-scholar'
        }),
        label='Google Scholar'
    )
    
    # SERP provider (hidden in Phase 1)
    serp_provider = forms.CharField(
        initial='google',
        widget=forms.HiddenInput()
    )
    
    class Meta:
        model = SearchStrategy
        fields = ['max_results']
        widgets = {
            'max_results': forms.NumberInput(attrs={
                'class': 'form-control',
                'style': 'width: 100px;',
                'min': 10,
                'max': 500,
                'id': 'max-results'
            })
        }
        labels = {
            'max_results': 'Maximum results per query'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-populate from existing search_config if editing
        if self.instance and self.instance.pk:
            config = self.instance.search_config or {}
            
            # Domains
            domains = config.get('domains', [])
            self.fields['domain_restrictions'].initial = '\n'.join(domains)
            
            # File types
            self.fields['file_types'].initial = config.get('file_types', [])
            
            # Search types
            search_types = config.get('search_types', ['web'])
            self.fields['search_web'].initial = 'web' in search_types
            self.fields['search_scholar'].initial = 'scholar' in search_types
    
    def clean_domain_restrictions(self):
        """Validate and parse domain restrictions"""
        domains_text = self.cleaned_data.get('domain_restrictions', '')
        if not domains_text:
            return []
        
        domains = []
        for line in domains_text.splitlines():
            domain = line.strip()
            if domain:
                # Basic domain validation
                if ' ' in domain or not '.' in domain:
                    raise ValidationError(f'Invalid domain: {domain}')
                domains.append(domain.lower())
        
        return domains
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        
        # Build search_config
        search_types = []
        if self.cleaned_data.get('search_web'):
            search_types.append('web')
        if self.cleaned_data.get('search_scholar'):
            search_types.append('scholar')
        
        instance.search_config = {
            'domains': self.cleaned_data.get('domain_restrictions', []),
            'file_types': self.cleaned_data.get('file_types', []),
            'search_types': search_types or ['web'],  # Default to web
            'serp_provider': 'google'  # Phase 1: always google
        }
        
        if commit:
            instance.save()
        
        return instance


class SessionDetailsForm(forms.Form):
    """Form for session name and description (header section)"""
    title = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg',
            'placeholder': 'e.g., Diabetes Management Guidelines Review',
            'id': 'session-title'
        }),
        label='Session Name'
    )
    
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Brief description of your systematic review objectives (optional)',
            'id': 'session-description'
        }),
        label='Description'
    )
```

---

## 🎨 **Views Implementation**

### Core Views

```python
# apps/search_strategy/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.http import JsonResponse
from django.contrib import messages
from django.utils import timezone
import json

from apps.review_manager.models import SearchSession, SessionActivity
from .models import SearchStrategy
from .forms import SearchStrategyForm, SessionDetailsForm

class DefineStrategyView(LoginRequiredMixin, View):
    """View for defining/editing search strategy with chip-based term input"""
    
    template_name = 'search_strategy/define_strategy.html'
    
    def get(self, request, session_id):
        session = get_object_or_404(SearchSession, id=session_id, created_by=request.user)
        
        # Get or create strategy
        strategy, created = SearchStrategy.objects.get_or_create(
            session=session,
            defaults={
                'created_by': request.user,
                'max_results': 50  # Default value
            }
        )
        
        # Initialize forms
        strategy_form = SearchStrategyForm(instance=strategy)
        session_form = SessionDetailsForm(initial={
            'title': session.title,
            'description': session.description
        })
        
        context = {
            'session': session,
            'strategy': strategy,
            'strategy_form': strategy_form,
            'session_form': session_form,
            'population_terms': json.dumps(strategy.population_terms),
            'interest_terms': json.dumps(strategy.interest_terms),
            'context_terms': json.dumps(strategy.context_terms),
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, session_id):
        session = get_object_or_404(SearchSession, id=session_id, created_by=request.user)
        strategy, _ = SearchStrategy.objects.get_or_create(
            session=session,
            defaults={'created_by': request.user}
        )
        
        # Handle different actions
        if 'action' in request.POST:
            action = request.POST['action']
            
            if action == 'save' or action == 'save_and_execute':
                # Update session details
                session_form = SessionDetailsForm(request.POST)
                if session_form.is_valid():
                    session.title = session_form.cleaned_data['title']
                    session.description = session_form.cleaned_data['description']
                    session.save()
                
                # Update strategy
                strategy_form = SearchStrategyForm(request.POST, instance=strategy)
                
                # Extract PIC terms from JSON
                strategy.population_terms = json.loads(request.POST.get('population_terms_json', '[]'))
                strategy.interest_terms = json.loads(request.POST.get('interest_terms_json', '[]'))
                strategy.context_terms = json.loads(request.POST.get('context_terms_json', '[]'))
                
                if strategy_form.is_valid():
                    strategy = strategy_form.save(commit=False)
                    strategy.save()
                    
                    # Update session status if strategy has terms
                    if strategy.has_any_terms() and session.status == 'draft':
                        session.status = 'strategy_ready'
                        session.save()
                        
                        # Log activity
                        SessionActivity.log_activity(
                            session=session,
                            action='STRATEGY_DEFINED',
                            description=f'Search strategy defined with {strategy.get_term_count()} terms',
                            user=request.user
                        )
                    
                    messages.success(request, 'Search strategy saved successfully!')
                    
                    if action == 'save_and_execute':
                        return redirect('serp_execution:execute', session_id=session.id)
                    else:
                        return redirect('review_manager:session_detail', session_id=session.id)
                else:
                    messages.error(request, 'Please correct the errors below.')
            
            elif action == 'cancel':
                # JavaScript handles confirmation for unsaved changes
                return redirect('review_manager:session_detail', session_id=session.id)
        
        # Re-render with current data
        context = {
            'session': session,
            'strategy': strategy,
            'strategy_form': SearchStrategyForm(request.POST, instance=strategy),
            'session_form': SessionDetailsForm(request.POST),
            'population_terms': request.POST.get('population_terms_json', '[]'),
            'interest_terms': request.POST.get('interest_terms_json', '[]'),
            'context_terms': request.POST.get('context_terms_json', '[]'),
        }
        
        return render(request, self.template_name, context)


class PreviewQueryView(LoginRequiredMixin, View):
    """AJAX endpoint for real-time query preview with formatting"""
    
    def post(self, request):
        if not request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid request'}, status=400)
        
        try:
            # Parse JSON data
            data = json.loads(request.body)
            
            population_terms = data.get('population_terms', [])
            interest_terms = data.get('interest_terms', [])
            context_terms = data.get('context_terms', [])
            file_types = data.get('file_types', [])
            domains = data.get('domains', [])
            
            # Generate query parts with highlighting info
            query_parts = []
            formatted_parts = []
            
            if population_terms:
                pop_query = ' OR '.join(f'"{term}"' for term in population_terms)
                query_parts.append(f'({pop_query})')
                formatted_parts.append({
                    'text': f'({pop_query})',
                    'type': 'population',
                    'label': 'Population'
                })
            
            if interest_terms:
                int_query = ' OR '.join(f'"{term}"' for term in interest_terms)
                query_parts.append(f'({int_query})')
                formatted_parts.append({
                    'text': f'({int_query})',
                    'type': 'interest',
                    'label': 'Interest/Intervention'
                })
            
            if context_terms:
                ctx_query = ' OR '.join(f'"{term}"' for term in context_terms)
                query_parts.append(f'({ctx_query})')
                formatted_parts.append({
                    'text': f'({ctx_query})',
                    'type': 'context',
                    'label': 'Context'
                })
            
            # Base query
            base_query = ' AND '.join(query_parts) if query_parts else ''
            
            # Add file types
            file_type_info = None
            if file_types and base_query:
                file_type_query = ' OR '.join(f'filetype:{ft}' for ft in file_types)
                file_type_info = f'({file_type_query})'
            
            # Generate URLs
            google_url = None
            scholar_url = None
            
            if base_query:
                import urllib.parse
                encoded_query = urllib.parse.quote(base_query)
                google_url = f"https://www.google.com/search?q={encoded_query}"
                scholar_url = f"https://scholar.google.com/scholar?q={encoded_query}"
            
            return JsonResponse({
                'preview': base_query or 'No search terms entered',
                'formatted_parts': formatted_parts,
                'file_type_filter': file_type_info,
                'domains': domains,
                'term_count': len([t for t in population_terms + interest_terms + context_terms if t]),
                'has_terms': bool(base_query),
                'google_url': google_url,
                'scholar_url': scholar_url
            })
            
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
```

---

## 🔗 **Integration Components**

### URL Configuration

```python
# apps/search_strategy/urls.py
from django.urls import path
from . import views

app_name = 'search_strategy'

urlpatterns = [
    path('<uuid:session_id>/define/', views.DefineStrategyView.as_view(), name='define'),
    path('preview/', views.PreviewQueryView.as_view(), name='preview_query'),
]
```

### Signal Handlers

```python
# apps/search_strategy/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import SearchStrategy
from apps.review_manager.models import SessionActivity

@receiver(post_save, sender=SearchStrategy)
def update_session_on_strategy_save(sender, instance, created, **kwargs):
    """Update session status when strategy is saved"""
    if instance.has_any_terms():
        session = instance.session
        if session.status == 'draft':
            session.status = 'strategy_ready'
            session.save()
            
            # Log activity
            SessionActivity.log_activity(
                session=session,
                action='STATUS_CHANGED',
                description='Session ready for search execution',
                user=instance.created_by,
                old_status='draft',
                new_status='strategy_ready'
            )
```

### App Configuration

```python
# apps/search_strategy/apps.py
from django.apps import AppConfig

class SearchStrategyConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.search_strategy'
    
    def ready(self):
        import apps.search_strategy.signals
```

---

## 🧪 **Testing Strategy**

### Test Coverage Requirements

```python
# apps/search_strategy/tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.review_manager.models import SearchSession
from .models import SearchStrategy
from .forms import SearchStrategyForm

User = get_user_model()

class SearchStrategyModelTests(TestCase):
    """Test SearchStrategy model functionality"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user
        )
        self.strategy = SearchStrategy.objects.create(
            session=self.session,
            created_by=self.user,
            population_terms=['elderly', 'older adults'],
            interest_terms=['diabetes management', 'insulin'],
            context_terms=['primary care', 'community']
        )
    
    def test_strategy_creation(self):
        """Test strategy is created correctly"""
        self.assertEqual(self.strategy.session, self.session)
        self.assertEqual(len(self.strategy.population_terms), 2)
        self.assertEqual(self.strategy.created_by, self.user)
    
    def test_empty_pic_categories_allowed(self):
        """Test that strategies can have empty PIC categories"""
        strategy = SearchStrategy.objects.create(
            session=self.session,
            created_by=self.user,
            population_terms=['elderly'],
            interest_terms=[],  # Empty
            context_terms=[],   # Empty
            max_results=50
        )
        
        self.assertTrue(strategy.has_any_terms())
        self.assertEqual(strategy.get_term_count(), 1)
    
    def test_generate_search_query(self):
        """Test Boolean query generation"""
        expected = '("elderly" OR "older adults") AND ("diabetes management" OR "insulin") AND ("primary care" OR "community")'
        self.assertEqual(self.strategy.generate_base_query(), expected)
    
    def test_search_configuration_flexibility(self):
        """Test various search configuration combinations"""
        strategy = SearchStrategy.objects.create(
            session=self.session,
            created_by=self.user,
            search_config={
                'domains': ['nice.org.uk', 'who.int'],
                'file_types': ['pdf'],
                'search_types': ['web', 'scholar'],
                'serp_provider': 'google'
            }
        )
        
        self.assertEqual(len(strategy.search_config['domains']), 2)
        self.assertIn('web', strategy.search_config['search_types'])
        self.assertIn('scholar', strategy.search_config['search_types'])
    
    def test_url_generation(self):
        """Test Google and Scholar URL generation"""
        google_url = self.strategy.get_google_search_url()
        self.assertIsNotNone(google_url)
        self.assertIn('google.com/search', google_url)
        self.assertIn('diabetes+management', google_url)
        
        scholar_url = self.strategy.get_scholar_search_url()
        self.assertIsNotNone(scholar_url)
        self.assertIn('scholar.google.com', scholar_url)


class SearchStrategyFormTests(TestCase):
    """Test form validation and behaviour"""
    
    def test_domain_validation(self):
        """Test domain restriction validation"""
        form_data = {
            'allowed_domains': 'nice.org.uk\ninvalid-domain-!@#\nwho.int',
            'max_results': 100
        }
        form = SearchStrategyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('domain_restrictions', form.errors)
    
    def test_max_results_validation(self):
        """Test max results boundaries"""
        # Test below minimum
        form = SearchStrategyForm(data={'max_results': 5})
        self.assertFalse(form.is_valid())
        
        # Test above maximum
        form = SearchStrategyForm(data={'max_results': 1000})
        self.assertFalse(form.is_valid())
        
        # Test valid range
        form = SearchStrategyForm(data={'max_results': 50})
        self.assertTrue(form.is_valid())


class SearchStrategyViewTests(TestCase):
    """Test view functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.session = SearchSession.objects.create(
            title='Test Session',
            status='draft',
            created_by=self.user
        )
    
    def test_define_strategy_view_get(self):
        """Test GET request to define strategy view"""
        url = reverse('search_strategy:define', kwargs={'session_id': self.session.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Population')
        self.assertContains(response, 'Interest')
        self.assertContains(response, 'Context')
        self.assertContains(response, 'chip')  # Check for chip UI
    
    def test_save_strategy_updates_session_status(self):
        """Test that saving a strategy updates session status"""
        url = reverse('search_strategy:define', kwargs={'session_id': self.session.id})
        
        response = self.client.post(url, {
            'action': 'save',
            'population_terms_json': '["elderly"]',
            'interest_terms_json': '["diabetes"]',
            'context_terms_json': '[]',
            'max_results': '50',
            'search_web': 'on',
            'serp_provider': 'google'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check session status updated
        self.session.refresh_from_db()
        self.assertEqual(self.session.status, 'strategy_ready')
    
    def test_ajax_preview_query(self):
        """Test AJAX query preview endpoint"""
        url = reverse('search_strategy:preview_query')
        
        response = self.client.post(
            url,
            data=json.dumps({
                'population_terms': ['elderly', 'seniors'],
                'interest_terms': ['diabetes'],
                'context_terms': ['hospital'],
                'file_types': ['pdf'],
                'domains': ['nice.org.uk']
            }),
            content_type='application/json',
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('preview', data)
        self.assertEqual(data['term_count'], 4)
        self.assertTrue(data['has_terms'])
        self.assertIsNotNone(data['google_url'])
    
    def test_permission_check(self):
        """Test users cannot access other users' strategies"""
        other_user = User.objects.create_user(
            username='otheruser',
            password='testpass123'
        )
        other_session = SearchSession.objects.create(
            title='Other Session',
            created_by=other_user
        )
        
        url = reverse('search_strategy:define', kwargs={'session_id': other_session.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class ChipUITests(TestCase):
    """Test chip-based UI specific functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.login(username='testuser', password='testpass123')
        self.session = SearchSession.objects.create(
            title='Test Session',
            created_by=self.user
        )
    
    def test_save_and_execute_action(self):
        """Test save and execute functionality"""
        url = reverse('search_strategy:define', kwargs={'session_id': self.session.id})
        
        response = self.client.post(url, {
            'action': 'save_and_execute',
            'population_terms_json': '["elderly"]',
            'interest_terms_json': '["diabetes"]',
            'context_terms_json': '["hospital"]',
            'max_results': '50',
            'search_web': 'on',
            'serp_provider': 'google'
        })
        
        # Should redirect to SERP execution
        self.assertEqual(response.status_code, 302)
        self.assertIn('serp_execution:execute', response.url)
    
    def test_mixed_search_types(self):
        """Test combination of web and scholar search"""
        strategy = SearchStrategy.objects.create(
            session=self.session,
            created_by=self.user,
            search_config={
                'search_types': ['web', 'scholar'],
                'domains': ['nice.org.uk'],
                'file_types': ['pdf', 'doc']
            }
        )
        
        # Verify both search types are stored
        self.assertIn('web', strategy.search_config['search_types'])
        self.assertIn('scholar', strategy.search_config['search_types'])
        
        # Verify both file types are stored
        self.assertEqual(len(strategy.search_config['file_types']), 2)
```

---

## 💻 **Frontend Implementation**

### Template Structure
The complete template implementation is provided in the previous artifact, featuring:

1. **Chip-based Term Management**
   - Visual chips with category-specific colours
   - Easy add/remove functionality
   - Enter key support

2. **Real-time Query Preview**
   - Syntax highlighting by PIC category
   - Live updates on term changes
   - Copy-to-clipboard functionality
   - Direct search engine links

3. **Responsive Design**
   - Mobile-friendly layout
   - Touch-friendly controls
   - Accessible form elements

### JavaScript Functionality
- Term management with dynamic chip creation
- AJAX-based query preview updates
- Unsaved changes confirmation
- Clipboard API integration

---

## 📋 **Implementation Checklist**

### Phase 1: Foundation (2-3 days)
- [ ] Create app structure and basic files
- [ ] Implement SearchStrategy and SearchQuery models
- [ ] Run initial migrations
- [ ] Set up basic admin interface

### Phase 2: Forms and Views (3-4 days)
- [ ] Implement SearchStrategyForm with validation
- [ ] Create DefineStrategyView with GET/POST handling
- [ ] Implement PreviewQueryView for AJAX
- [ ] Add URL routing

### Phase 3: Frontend (3-4 days)
- [ ] Create define_strategy.html template
- [ ] Implement chip-based UI with JavaScript
- [ ] Add real-time preview functionality
- [ ] Style with existing CSS framework

### Phase 4: Integration (2-3 days)
- [ ] Connect with SessionActivity logging
- [ ] Implement status update signals
- [ ] Test integration with review_manager
- [ ] Add permission checks

### Phase 5: Testing (2-3 days)
- [ ] Write model tests
- [ ] Write form validation tests
- [ ] Write view tests
- [ ] Test AJAX functionality
- [ ] Cross-browser testing

### Phase 6: Documentation (1 day)
- [ ] Code documentation
- [ ] User guide
- [ ] API documentation for SERP execution integration

**Total Estimated Time: 14-18 days**

---

## 🚀 **Deployment Considerations**

### Performance Optimisations
1. **Database Indexing**
   - Index on session relationship
   - Consider GIN index for ArrayField searches

2. **Caching Strategy**
   - Cache generated queries
   - Cache preview responses

3. **Frontend Performance**
   - Debounce preview updates
   - Lazy load chip management

### Security Measures
1. **Input Validation**
   - Server-side term validation
   - Domain restriction validation
   - XSS prevention in preview

2. **Access Control**
   - User can only access own strategies
   - CSRF protection on all forms
   - Rate limiting on AJAX endpoints

### Monitoring
1. **Error Tracking**
   - Log failed query generations
   - Track AJAX errors
   - Monitor performance metrics

2. **Usage Analytics**
   - Track term usage patterns
   - Monitor search type preferences
   - Analyse strategy completion rates

---

## 📚 **Appendices**

### A. Database Migration Script
```python
# Generated migration will include:
- ArrayField for PIC terms
- JSONField for configuration
- Indexes for performance
- Foreign key to SearchSession
```

### B. Sample Data for Testing
```python
# Management command: create_sample_strategies
- Various PIC term combinations
- Different search configurations
- Edge cases (empty categories, special characters)
```

### C. API Documentation for SERP Execution
```python
# Expected interface:
{
    "strategy_id": "uuid",
    "queries": [
        {
            "query_string": "generated query",
            "search_type": "web|scholar",
            "max_results": 50,
            "domains": ["list of domains"],
            "file_types": ["pdf", "doc"]
        }
    ]
}
```

---
