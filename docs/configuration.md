# Configuration

Dj Urls Panel currently works out of the box with minimal configuration.

For access control specifically (locking down individual views or MCP tools by group), see [Scopes](scopes.md).

## Basic Setup

The only required configuration is adding the app to your `INSTALLED_APPS` and including the URLs in your URL configuration.

See the [Installation](installation.md) guide for setup instructions.

## URLs Configuration

```python
# urls.py
urlpatterns = [
    path('admin/dj-urls-panel/', include('dj_urls_panel.urls')),  # Custom path
    path('admin/', admin.site.urls),
]
```

## URL Filtering & Testing Settings

### `EXCLUDE_URLS`

**Type:** `list[str]`  
**Default:** `[]`  
**Description:** Regex patterns for URL paths to hide from the panel entirely.

```python
DJ_URLS_PANEL_SETTINGS = {
    'EXCLUDE_URLS': [
        r'^admin/',          # Exclude admin URLs
        r'^__debug__/',      # Exclude debug toolbar
        r'^api/internal/',   # Exclude internal APIs
    ],
}
```

### `URL_CONFIG`

**Type:** `str | None`  
**Default:** `None`  
**Description:** Use a custom URLconf module instead of `ROOT_URLCONF`. Useful for showing only a subset of URLs (e.g. just an API surface).

```python
DJ_URLS_PANEL_SETTINGS = {
    'URL_CONFIG': 'myproject.api_urls',
}
```

### `ENABLE_TESTING`

**Type:** `bool`  
**Default:** `True`  
**Description:** Enables the Swagger-like URL testing interface (execute requests directly from the admin). Disable for a read-only, introspection-only panel.

```python
DJ_URLS_PANEL_SETTINGS = {
    'ENABLE_TESTING': False,
}
```

When disabled, the testing interface is hidden and the execute endpoint returns `403`.

### `ALLOWED_HOSTS`

**Type:** `list[str] | None`  
**Default:** `None`  
**Description:** SSRF protection for the testing interface. `None` relies on the default blocklist (localhost, private/link-local IP ranges). Set a list to allow **only** those hosts.

```python
DJ_URLS_PANEL_SETTINGS = {
    'ALLOWED_HOSTS': ['example.com', 'api.example.com'],
}
```

### Production Recommendations

```python
DJ_URLS_PANEL_SETTINGS = {
    'ENABLE_TESTING': False,  # Disable testing interface entirely
    # OR, if you need testing in production:
    'ALLOWED_HOSTS': ['yourdomain.com'],  # Whitelist only your domains
}
```

## Security

Dj Urls Panel uses Django's built-in admin authentication:

- Only staff users (`is_staff=True`) can access the panel
- All views require authentication via `@staff_member_required`
- No additional security configuration needed beyond the settings above

## CSS Customization

### `LOAD_DEFAULT_CSS`

**Type:** `bool`  
**Default:** `True`  
**Description:** Whether to load the built-in URLs Panel stylesheet. Set to `False` to use your own styles from scratch.

### `EXTRA_CSS`

**Type:** `list[str]`  
**Default:** `[]`  
**Description:** Additional stylesheets to load after the default CSS. Accepts static file paths or full URLs.

Static file paths are **relative to your app's `static/` subdirectory** (same convention as Django's `{% static %}` tag). A file at `myapp/static/myapp/css/overrides.css` is referenced as `myapp/css/overrides.css`.

```python
DJ_URLS_PANEL_SETTINGS = {
    'LOAD_DEFAULT_CSS': True,
    'EXTRA_CSS': [
        # File lives at: myapp/static/myapp/css/overrides.css
        'myapp/css/overrides.css',
        # Full URLs are also supported
        'https://cdn.example.com/theme.css',
    ],
}
```

## Panel Tools (MCP)

Dj Urls Panel ships `dj_urls_panel/tools.py`, a `ToolRegistry` of MCP-facing tools (`list_urls`, `get_url_detail`, `inspect_view`) that [dj-control-room](https://github.com/django-control-room/dj-control-room) aggregates and exposes to AI agents over its MCP endpoint. See [Features → MCP Tools](features.md#mcp-tools-ai-agent-integration) for the full tool reference.

### `SHOW_SOURCE`

**Type:** `bool`  
**Default:** `False`  
**Description:** When `True`, the `inspect_view` tool includes a source code preview (up to 20 lines) in its results. Leave `False` to return metadata only.

```python
DJ_URLS_PANEL_SETTINGS = {
    'SHOW_SOURCE': True,
}
```

### `SCOPE_PERMISSIONS`

**Type:** `dict`  
**Default:** `{}`  
**Description:** Restrict individual tool scopes (or view scopes) independently of the panel's default permission checks. Each of the three panel tools ships under its own scope (`agent_url_list`, `agent_url_detail`, `agent_inspect_view`), separate from the view scopes humans hit in the admin UI, so agent access can be governed independently.

```python
DJ_URLS_PANEL_SETTINGS = {
    'SCOPE_PERMISSIONS': {
        'agent_inspect_view': {'allowed_groups': ['ai-agents']},
    },
}
```

See [Scopes](scopes.md) for the full list of view and tool scopes, and the [dj-control-room-base Panel Tools guide](https://django-control-room.github.io/dj-control-room-base/building-panels/#panel-tools) for the underlying API.
