# Dj Urls Panel

  <img src="https://raw.githubusercontent.com/django-control-room/dj-urls-panel/main/images/dj-urls-panel.png" alt="Dj Urls Panel Logo" width="700">

  <strong>Django admin URL introspection. Inspect, search, and understand your project's URL routing, directly from the admin.</strong>

## Overview

Dj Urls Panel is a Django admin extension that provides a comprehensive interface for viewing and testing your Django URLs. It includes a Swagger-like testing interface, automatic Django REST Framework integration, and built-in security features.

## Features

- **URL Visualization**: View all Django URL patterns in an organized, searchable interface
- **Interactive Testing Interface**: Swagger-like UI for testing URLs directly from the admin:
  - Test any HTTP method (GET, POST, PUT, PATCH, DELETE, etc.)
  - Dynamic URL parameter input with validation
  - Configure headers and authentication (Bearer, Token, Basic, Session)
  - Request body editor with JSON formatting
  - Real-time response display
  - Automatic cURL command generation with copy functionality
- **DRF Integration**: Automatic detection and visualization of Django REST Framework serializers
- **Security Features**:
  - Built-in SSRF protection with configurable blocklist
  - Optional host whitelisting for production
  - Ability to disable testing interface entirely
- **Admin Panel Integration**: Seamlessly integrated into Django Admin
- **AI Agent Integration (MCP)**: Exposes `list_urls`, `get_url_detail`, and `inspect_view` tools to AI agents via dj-control-room's MCP server

## Quick Links

- [Features](https://django-control-room.github.io/dj-urls-panel/features/) - Explore all features with screenshots
- [Installation](https://django-control-room.github.io/dj-urls-panel/installation/) - Get started in minutes
- [Configuration](https://django-control-room.github.io/dj-urls-panel/configuration/) - Customize for your needs
- [Scopes](https://django-control-room.github.io/dj-urls-panel/scopes/) - Lock down specific views or MCP tools
- [Contributing](https://django-control-room.github.io/dj-urls-panel/contributing/) - Contribute to the project

## Requirements

- Python 3.9+
- Django 4.2+

## License

MIT License - See [LICENSE](https://github.com/django-control-room/dj-urls-panel/blob/main/LICENSE) file for details.
