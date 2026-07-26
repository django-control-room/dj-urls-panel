from __future__ import annotations

import importlib
import inspect

from dj_control_room_base.core.panel_tool import (
    PanelToolContext,
    PanelToolResult,
    ToolRegistry,
)

from .utils import UrlListInterface

registry = ToolRegistry()


@registry.register(
    name="list_urls",
    scope="introspect",
    description=(
        "List every URL pattern Dj Urls Panel can see, with its name, "
        "view, namespace, and allowed HTTP methods."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "namespace": {
                "type": "string",
                "description": "Filter to URLs in this namespace (use '_root' for URLs with no namespace).",
            },
            "query": {
                "type": "string",
                "description": "Case-insensitive substring filter over the pattern, name, and view.",
            },
            "http_method": {
                "type": "string",
                "description": "Filter to URLs whose view supports this HTTP method, e.g. 'POST'.",
            },
        },
    },
)
def handle_list_urls(ctx: PanelToolContext) -> PanelToolResult:
    """List every URL pattern DCR can see, with name/view/namespace/http methods."""
    args = {
        "namespace": ctx.inputs.get("namespace", "").strip(),
        "query": ctx.inputs.get("query", "").strip(),
        "http_method": ctx.inputs.get("http_method", "").strip(),
    }

    urls = UrlListInterface().filter_urls(
        namespace=args["namespace"] or None,
        query=args["query"] or None,
        http_method=args["http_method"] or None,
    )

    items = [_compact_url_entry(entry) for entry in urls]
    items.sort(key=lambda item: item["pattern"])

    return PanelToolResult(
        success=True,
        message=f"{len(items)} URL(s) found.",
        data={"urls": items},
    )


@registry.register(
    name="get_url_detail",
    scope="introspect",
    description=(
        "Get full detail for URL(s) - view, view class, namespace, HTTP "
        "methods, URL parameters, and DRF serializer info (if any). Look "
        "up by exact 'name' or 'pattern' (matches at most one URL), or "
        "reverse-lookup by 'view' (dotted path or bare name, e.g. "
        "'api.views.ArticleViewSet') to find every URL routed to it."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "URL name, e.g. 'admin:login' or 'api:article-list'.",
            },
            "pattern": {
                "type": "string",
                "description": "Exact URL pattern, e.g. '/api/articles/<int:pk>/'.",
            },
            "view": {
                "type": "string",
                "description": "Dotted view path (e.g. 'api.views.ArticleViewSet') or bare name (e.g. 'ArticleViewSet'); returns every URL routed to it.",
            },
        },
    },
)
def handle_get_url_detail(ctx: PanelToolContext) -> PanelToolResult:
    """Full detail for URL(s), looked up by name, pattern, or view."""
    args = {
        "name": ctx.inputs.get("name", "").strip(),
        "pattern": ctx.inputs.get("pattern", "").strip(),
        "view": ctx.inputs.get("view", "").strip(),
    }

    if not args["name"] and not args["pattern"] and not args["view"]:
        return PanelToolResult(
            success=False,
            message="Provide 'name', 'pattern', or 'view' to look up a URL.",
        )

    interface = UrlListInterface()

    if args["name"]:
        identifier = args["name"]
        entry = interface.get_url_by_name(identifier)
        matches = [entry] if entry else []
    elif args["pattern"]:
        identifier = args["pattern"]
        entry = interface.get_url_by_pattern(identifier)
        matches = [entry] if entry else []
    else:
        identifier = args["view"]
        matches = interface.get_urls_by_view(identifier)

    if not matches:
        return PanelToolResult(
            success=False, message=f"No URL found matching '{identifier}'."
        )

    return PanelToolResult(
        success=True,
        message=f"{len(matches)} URL(s) matched '{identifier}'.",
        data={"urls": matches},
    )


@registry.register(
    name="inspect_view",
    scope="introspect",
    description=(
        "Resolve a view's dotted path to its source file/line (and any URL "
        "patterns currently routed to it), so an agent can jump straight to "
        "the view instead of grepping."
    ),
    input_schema={
        "type": "object",
        "properties": {
            "dotted_path": {
                "type": "string",
                "description": "Dotted path to the view function or class, e.g. 'api.views.ArticleViewSet'.",
            },
        },
        "required": ["dotted_path"],
    },
)
def handle_inspect_view(ctx: PanelToolContext) -> PanelToolResult:
    """Resolve a view's dotted path to its source location so an agent can jump straight to it."""
    dotted_path = ctx.inputs.get("dotted_path", "").strip()
    if not dotted_path:
        return PanelToolResult(
            success=False,
            message="'dotted_path' is required, e.g. 'api.views.ArticleViewSet'.",
        )

    obj, resolved_module = _resolve_dotted(dotted_path)
    if obj is None:
        return PanelToolResult(
            success=False,
            message=f"Could not resolve '{dotted_path}' to an importable object.",
        )

    if not callable(obj):
        return PanelToolResult(
            success=False,
            message=f"'{dotted_path}' resolved to a non-callable {type(obj).__name__}.",
        )

    try:
        source_file = inspect.getfile(obj)
    except (TypeError, OSError):
        source_file = None

    try:
        lines, source_line = inspect.getsourcelines(obj)
    except (TypeError, OSError):
        lines, source_line = None, None

    source_preview = None
    if lines is not None and ctx.config.get_settings("SHOW_SOURCE"):
        max_lines = 20
        source_preview = "".join(lines[:max_lines])
        if len(lines) > max_lines:
            source_preview += f"\n    # ... ({len(lines) - max_lines} more lines)"

    connected_urls = [
        _compact_url_entry(entry)
        for entry in UrlListInterface().get_urls_by_view(dotted_path)
    ]

    data = {
        "dotted_path": dotted_path,
        "resolved_module": resolved_module,
        "kind": "class" if inspect.isclass(obj) else "function",
        "qualname": getattr(obj, "__qualname__", getattr(obj, "__name__", dotted_path)),
        "module": getattr(obj, "__module__", resolved_module),
        "source_file": source_file,
        "source_line": source_line,
        "source_preview": source_preview,
        "docstring": inspect.getdoc(obj),
        "connected_urls": connected_urls,
    }

    location = f" at {source_file}:{source_line}" if source_file else ""
    return PanelToolResult(
        success=True,
        message=f"Resolved '{dotted_path}'{location}.",
        data=data,
    )


def _compact_url_entry(entry: dict) -> dict:
    """Trim a UrlListInterface entry down to the fields tools return by default."""
    serializer_info = entry.get("serializer_info")
    return {
        "pattern": entry["pattern"],
        "name": entry["name"],
        "view": entry["view"],
        "view_class": entry["view_class"],
        "namespace": entry["namespace"],
        "http_methods": entry["http_methods"],
        "url_parameters": entry["url_parameters"],
        "has_serializer": bool(
            serializer_info and serializer_info.get("has_serializer")
        ),
        "serializer_name": serializer_info.get("serializer_name")
        if serializer_info
        else None,
    }


def _resolve_dotted(dotted_path: str):
    """
    Resolve a dotted path to an object, trying the longest importable module
    prefix first and walking the remainder via getattr (handles both plain
    module-level functions and classes).
    """
    parts = dotted_path.split(".")
    for i in range(len(parts) - 1, 0, -1):
        module_path = ".".join(parts[:i])
        try:
            mod = importlib.import_module(module_path)
        except Exception:
            continue

        obj = mod
        try:
            for attr in parts[i:]:
                obj = getattr(obj, attr)
        except AttributeError:
            continue

        return obj, module_path

    return None, None
