# Scopes

Dj Urls Panel splits its permission checks into **scopes**: named checkpoints passed to `@panel_config.permission_required(scope)` (for views) and `scope=` (for panel tools). Every scope inherits the panel-wide `ALLOWED_GROUPS`/`REQUIRE_SUPERUSER` rule by default; a scope only behaves differently once you add an entry for it under `SCOPE_PERMISSIONS` in `DJ_URLS_PANEL_SETTINGS`.

Both views and tools are enforced through the **exact same mechanism**: the same `SCOPE_PERMISSIONS` dict, the same `ALLOWED_GROUPS`/`REQUIRE_SUPERUSER` keys, the same resolution order. There is no separate permission system for AI agents. See the [Permissions and Scopes guide](https://djangocontrolroom.com/guides/control-room-permissions-and-scopes) for the full model.

## Design: separate scopes per actor type

Unlike some panels where a tool reuses the same scope as its corresponding view, Dj Urls Panel deliberately gives **humans (admin UI views)** and **AI agents (MCP tools)** distinct scopes, even where a tool mirrors a view's data. This means you can grant staff full browsing access in the admin while denying (or separately restricting) automated/agent access to the same data, or vice versa, without one setting accidentally controlling both.

## Reference

| Scope | Type | Protects | Default behavior |
|---|---|---|---|
| `url_list` | View | `index` view: browse/search the full URL list | Any staff user |
| `url_detail` | View | `url_detail` view: a single URL's detail page | Any staff user |
| `url_execute` | View | `ExecuteRequestView`: fires a live HTTP request against a route | Any staff user (recommend restricting in production, see below) |
| `agent_url_list` | Tool | `list_urls` MCP tool | Any staff user the MCP endpoint authenticates as |
| `agent_url_detail` | Tool | `get_url_detail` MCP tool | Any staff user the MCP endpoint authenticates as |
| `agent_inspect_view` | Tool | `inspect_view` MCP tool (optionally includes source code via `SHOW_SOURCE`) | Any staff user the MCP endpoint authenticates as |

## Example: independent human vs. agent access

```python
DJ_URLS_PANEL_SETTINGS = {
    # Panel-wide default: any staff member can use the admin UI
    'ALLOWED_GROUPS': [],

    'SCOPE_PERMISSIONS': {
        # Only a dedicated group may fire live test requests from the admin
        'url_execute': {'ALLOWED_GROUPS': ['platform-admins']},

        # AI agents may list/inspect URLs, but may not see source code
        # previews or call get_url_detail, even though staff can browse
        # the equivalent admin pages freely.
        'agent_inspect_view': {'ALLOWED_GROUPS': ['ai-agents-readonly']},
        'agent_url_detail': {'ALLOWED_GROUPS': []},
    },
}
```

Any scope not mentioned in `SCOPE_PERMISSIONS` simply falls back to the panel-wide rule, so you only ever need to write down the exceptions.

See [Configuration](configuration.md#url-filtering-testing-settings) for the rest of the panel's settings, and [Features → MCP Tools](features.md#mcp-tools-ai-agent-integration) for what each tool does.
