# Installation

## 1. Install the Package

```bash
pip install dj-urls-panel dj-control-room
```

## 2. Add to Django Settings

Add `dj_urls_panel` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'dj_control_room_base',  # core lib must be included
    'dj_urls_panel',  # add panel here.
    'dj_control_room', # hub package for Django control room
    # ... your other apps
]
```

## 3. Include URLs

Add the Panel URLs to your main `urls.py`:

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/dj-control-room-base/', include('dj_control_room_base.urls')),
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),
    path('admin/dj-control-room/')
    path('admin/', admin.site.urls),
]
```

## 4. Run Migrations

```bash
python manage.py migrate
```

## 5. Configure Settings (Optional)

For basic usage, no configuration is needed. `DJ_URLS_PANEL_SETTINGS` in your `settings.py` lets you exclude URL patterns, swap the URLconf, and lock down (or disable) the testing interface for production.

See [Configuration](configuration.md) for the full settings reference and security recommendations.

## 6. Access the Panel

1. Start your Django development server:
   ```bash
   python manage.py runserver
   ```

2. Navigate to `http://127.0.0.1:8000/admin/`

3. Look for the "DJ URLS PANEL" section

That's it! You can now browse and test your URLs directly from the admin interface.
