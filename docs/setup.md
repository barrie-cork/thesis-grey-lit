# Thesis Grey Django Project - Handover and Environment Guide

This document outlines the setup and configuration of the Thesis Grey Django project. It includes folder structure, environment setup, and instructions for working with different settings modes (local/production).

---

## ✅ Project Overview

* **Framework:** Django 4.2
* **Language:** Python 3.12
* **Dev Environment:** WSL2 (Ubuntu) on Windows
* **Database:** PostgreSQL (via Docker)
* **Task Queue:** Celery with Redis (via Docker)
* **Frontend:** Django Templates + Static assets (CSS/JS)
* **Folder location:** `D:\Python\Projects\thesis-grey-lit`
* **AI Compatibility:** Project files are located on a Windows drive to support Claude Desktop and other local AI tools.

---

## ✅ Folder Structure

```
thesis-grey-lit/
├── manage.py
├── requirements.txt
├── docker-compose.yml
├── .env
├── static/
├── templates/
│   └── base.html
├── apps/
│   ├── accounts/
│   ├── review_manager/
│   ├── search_strategy/
│   ├── serp_execution/
│   ├── results_manager/
│   ├── review_results/
│   └── reporting/
├── thesis_grey_project/
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── local.py
│   │   └── production.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
└── venv/ (virtual environment)
```

---

## ✅ Environment Setup

### 1. Activate WSL and Virtual Environment

```bash
cd /mnt/d/Python/Projects/thesis-grey-lit
source venv/bin/activate
```

### 2. Start Docker Services (PostgreSQL + Redis)

```bash
docker compose up -d
```

### 3. Run Django Server

```bash
python3 manage.py runserver
```

Server runs at: [http://localhost:8000](http://localhost:8000)

### 4. Create Superuser (first-time only)

```bash
python3 manage.py createsuperuser
```

---

## ✅ Using Split Django Settings

### Switching Between Settings Modes

By default, Django is configured to use `local.py` via:

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thesis_grey_project.settings.local")
```

### Available Settings Files:

* `base.py`: shared settings (used by all environments)
* `local.py`: development mode (`DEBUG=True`, local DB, localhost-only)
* `production.py`: production-ready (`DEBUG=False`, real secrets, domain-hosted)

To switch environments:

* **In development**: nothing needed (uses `local.py`)
* **For production**: change the `DJANGO_SETTINGS_MODULE` value in:

  * `manage.py`
  * `wsgi.py`
  * `asgi.py`

```python
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "thesis_grey_project.settings.production")
```

---

## ✅ Celery Setup

Celery is used to handle background tasks (e.g., search execution, result processing).

### 1. Configuration in `settings/base.py`

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
```

### 2. Create `celery.py` in `thesis_grey_project/`

```python
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'thesis_grey_project.settings.local')

app = Celery('thesis_grey_project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

### 3. Modify `__init__.py` in `thesis_grey_project/`

```python
from .celery import app as celery_app

__all__ = ('celery_app',)
```

### 4. Run the Celery worker

```bash
celery -A thesis_grey_project worker --loglevel=info
```

This connects to Redis and executes tasks from any app using the `@shared_task` decorator or standard Celery task registration.

---

## ✅ Getting Started for New Collaborators

1. **Clone the repository** to your machine (make sure Docker and WSL2 are set up):

```bash
git clone <repo_url>
cd thesis-grey-lit
```

2. **Activate WSL and Python virtual environment**:

```bash
source venv/bin/activate
```

3. **Install Python dependencies**:

```bash
pip install -r requirements.txt
```

4. **Start Docker containers (PostgreSQL + Redis)**:

```bash
docker compose up -d
```

5. **Run migrations and start the development server**:

```bash
python3 manage.py migrate
python3 manage.py runserver
```

6. **(Optional)**: Start Celery worker for background tasks:

```bash
celery -A thesis_grey_project worker --loglevel=info
```

You're now ready to begin development, contribute to apps, and explore the project structure!

---

## ✅ README Template for Each App

In each `apps/<app_name>/` folder, create a `README.md` file using this template:

### Template: `apps/<app_name>/README.md`

```markdown
# <App Name>

Part of the Thesis Grey Django project.

## 📦 Purpose
Describe what this app does. Example:
> The `search_strategy` app allows users to define and edit structured search strategies using the PIC framework.

## 📁 Key Files
- `models.py`: Database models
- `views.py`: Views (CBVs or function-based)
- `forms.py`: Django forms
- `urls.py`: App-level URL routing
- `templates/<app_name>/`: App-specific templates

## ✅ Setup Notes
Make sure this app is included in `INSTALLED_APPS` as `apps.<app_name>`.

## 🛠 Development Tasks
List current todos or dev notes for this app.

## 🔗 Related Apps
Mention other apps it interacts with (e.g., `review_manager`, `serp_execution`).
```

Create a README like this inside each of:

* `apps/accounts/`
* `apps/review_manager/`
* `apps/search_strategy/`
* `apps/serp_execution/`
* `apps/results_manager/`
* `apps/review_results/`
* `apps/reporting/`
