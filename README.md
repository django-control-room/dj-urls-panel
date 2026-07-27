[![Django Control Room Panel](https://img.shields.io/badge/Django%20Control%20Room-Panel-0c4b33?logo=django)](https://github.com/django-control-room/dj-control-room)
[![Tests](https://github.com/django-control-room/dj-urls-panel/actions/workflows/test.yml/badge.svg)](https://github.com/django-control-room/dj-urls-panel/actions/workflows/test.yml)
[![codecov](https://codecov.io/gh/django-control-room/dj-urls-panel/branch/main/graph/badge.svg)](https://codecov.io/gh/django-control-room/dj-urls-panel)
[![PyPI version](https://badge.fury.io/py/dj-urls-panel.svg)](https://badge.fury.io/py/dj-urls-panel)
[![Python versions](https://img.shields.io/pypi/pyversions/dj-urls-panel.svg)](https://pypi.org/project/dj-urls-panel/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Downloads](https://img.shields.io/pypi/dm/dj-urls-panel.svg)](https://pypi.org/project/dj-urls-panel/)


# Dj Urls Panel

Django admin URL introspection. Inspect, search, and understand your project's URL routing, directly from the admin.

![DJ Urls Panel](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/dj-urls-panel.png)


## Docs

[https://django-control-room.github.io/dj-urls-panel/](https://django-control-room.github.io/dj-urls-panel/)

## Features

- **URL Visualization**: View all Django URL patterns in an organized, searchable interface
- **URL Testing Interface**: Swagger-like interface for testing URLs with:
  - HTTP method selection (GET, POST, PUT, PATCH, DELETE, etc.)
  - Dynamic URL parameter input
  - Header specification
  - Authentication support (Bearer, Token, Basic Auth, Session)
  - Request body editor with JSON formatting
  - Live cURL command generation with copy functionality
  - Real-time response display with headers and body
- **DRF Integration**: Automatic detection and visualization of Django REST Framework serializers
- **Security Features**:
  - Configurable SSRF protection with default blocklist for internal IPs
  - Optional host whitelisting for production environments
  - Ability to disable testing interface entirely
- **Search & Filter**: Search URLs by pattern, name, or view function
- **Namespace Support**: Filter and organize URLs by namespace
- **AI Agent Integration (MCP)**: Exposes `list_urls`, `get_url_detail`, and `inspect_view` tools so AI agents (Cursor, Claude, etc.) can introspect your URL routing via [dj-control-room](https://github.com/django-control-room/dj-control-room)'s MCP server


## Requirements

- Python 3.9+
- Django 4.2+


## Screenshots

### Django Admin Integration
Seamlessly integrated into your Django admin interface. A new section for dj-urls-panel
will appear in the same places where your models appear.

**NOTE:** This application does not actually introduce any model or migrations.

![Admin Home](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_home.png)

### URL List View
Browse all URLs in your Django project with detailed information about patterns, views, and namespaces.

![URL List](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_url_list.png)

### URL Detail & Testing Interface
View detailed information about each URL and test it directly from the admin interface.

![URL Detail](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_url_detail.png)

### DRF Serializer Information
Automatic detection and visualization of Django REST Framework serializers with field details.

![Serializer Info](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_url_serializaer.png)

### URL Metadata & Usage Examples
View URL metadata and get code examples for using URLs in your Django views.

![URL Metadata](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_url_meta.png)

![Usage Examples](https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/admin_url_usage.png)


## Installation

```bash
pip install dj-urls-panel dj-control-room
```

Add it to `INSTALLED_APPS`, include its URLs, and migrate:

```python
INSTALLED_APPS = [
    # ...
    'dj_control_room_base',
    'dj_urls_panel',
    'dj_control_room',
    # ...
]
```

```python
urlpatterns = [
    path('admin/dj-control-room-base/', include('dj_control_room.urls')),
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),
    path('admin/dj-control-room/', include('dj_control_room.urls'),)
    path('admin/', admin.site.urls),
]
```

```bash
python manage.py migrate
```

Then visit `/admin/` and look for the "DJ URLS PANEL" section.

For the full walkthrough, settings reference (URL filtering, testing/SSRF security, CSS), and production recommendations, see the [Installation](https://django-control-room.github.io/dj-urls-panel/installation/) and [Configuration](https://django-control-room.github.io/dj-urls-panel/configuration/) docs.


## MCP Tools (AI Agent Integration)

Ships `list_urls`, `get_url_detail`, and `inspect_view` tools that [dj-control-room](https://github.com/django-control-room/dj-control-room)'s MCP server exposes to AI agents (Cursor, Claude, etc.), so they can look up URL routing, DRF serializer info, and view source locations without grepping your codebase.

See [Features → MCP Tools](https://django-control-room.github.io/dj-urls-panel/features/#mcp-tools-ai-agent-integration) for the full tool reference and [Scopes](https://django-control-room.github.io/dj-urls-panel/scopes/) for how agent access is permissioned separately from the admin UI.


## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

## Development Setup

Want to contribute or set up the project for local development? See [docs/contributing.md](docs/contributing.md) for prerequisites, Docker/virtualenv setup, running the example project, and the test suite.
