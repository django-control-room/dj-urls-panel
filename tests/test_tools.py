"""
Tests for the MCP introspection tools exposed via conf.py's `tools=[...]`.

Handlers are called directly with a PanelToolContext (bypassing the MCP
transport/registry, which is exercised separately in dj-control-room).
Fixture data comes from `example_project/api/{urls,views}.py`, resolved
through `ROOT_URLCONF` (see `DJ_URLS_PANEL_SETTINGS` in
`example_project/example_project/settings.py`, which excludes anything under
`admin/` and points `URL_CONFIG` at `example_project.urls`):

- api:health              -> api.views.HealthCheckView   (GET only)
- api:generic-article-list -> api.views.ArticleListCreateView (GET, POST)
- api:func-article-list    -> api.views.article_list      (GET, POST; FBV)
- api:article-list/-detail/-publish/-unpublish/-published
                            -> api.views.ArticleViewSet (router, one view class
                               backing several distinct URL patterns)
"""

from django.test import override_settings

from dj_control_room_base.core.panel_tool import PanelToolContext

from dj_urls_panel.conf import panel_config
from dj_urls_panel.tools import (
    handle_get_url_detail,
    handle_inspect_view,
    handle_list_urls,
)

from .base import UrlsPanelTestCase

HEALTH_NAME = "api:health"
HEALTH_PATTERN = "/api/health/"
GENERIC_ARTICLE_LIST_NAME = "api:generic-article-list"
FUNC_ARTICLE_LIST_NAME = "api:func-article-list"


def _ctx(**inputs) -> PanelToolContext:
    return PanelToolContext(user=None, inputs=inputs, config=panel_config)


class TestListUrls(UrlsPanelTestCase):
    def test_returns_success(self):
        result = handle_list_urls(_ctx())
        self.assertTrue(result.success)

    def test_includes_api_urls(self):
        result = handle_list_urls(_ctx())
        names = {u["name"] for u in result.data["urls"]}
        self.assertIn(HEALTH_NAME, names)
        self.assertIn(GENERIC_ARTICLE_LIST_NAME, names)

    def test_admin_urls_excluded_by_default_settings(self):
        """DJ_URLS_PANEL_SETTINGS excludes anything under 'admin/'."""
        result = handle_list_urls(_ctx())
        for url in result.data["urls"]:
            self.assertFalse(url["pattern"].lstrip("/").startswith("admin/"))

    def test_namespace_filter(self):
        result = handle_list_urls(_ctx(namespace="api"))
        self.assertTrue(result.data["urls"])
        for url in result.data["urls"]:
            self.assertEqual(url["namespace"], "api")

    def test_namespace_filter_no_match_returns_empty(self):
        result = handle_list_urls(_ctx(namespace="no_such_namespace"))
        self.assertEqual(result.data["urls"], [])

    def test_query_filter_matches_name_substring(self):
        result = handle_list_urls(_ctx(query="health"))
        names = {u["name"] for u in result.data["urls"]}
        self.assertEqual(names, {HEALTH_NAME})

    def test_query_filter_no_match_returns_empty(self):
        result = handle_list_urls(_ctx(query="no_such_url_xyz"))
        self.assertEqual(result.data["urls"], [])

    def test_http_method_filter_includes_matching(self):
        result = handle_list_urls(_ctx(http_method="post"))
        names = {u["name"] for u in result.data["urls"]}
        self.assertIn(GENERIC_ARTICLE_LIST_NAME, names)
        self.assertIn(FUNC_ARTICLE_LIST_NAME, names)

    def test_http_method_filter_excludes_non_matching(self):
        result = handle_list_urls(_ctx(http_method="POST"))
        names = {u["name"] for u in result.data["urls"]}
        self.assertNotIn(HEALTH_NAME, names)

    def test_view_class_populated_for_drf_api_view_function(self):
        """DRF's @api_view wraps a plain function in a dynamically generated
        APIView subclass, so the *view* field lands on that generic wrapper
        while view_class carries the useful dotted path back to the actual
        decorated function."""
        result = handle_list_urls(_ctx(query="func-article-list"))
        url = next(u for u in result.data["urls"] if u["name"] == FUNC_ARTICLE_LIST_NAME)
        self.assertEqual(url["view_class"], "api.views.article_list")

    def test_view_class_populated_for_class_based_view(self):
        result = handle_list_urls(_ctx(query="health"))
        url = next(u for u in result.data["urls"] if u["name"] == HEALTH_NAME)
        self.assertEqual(url["view_class"], "api.views.HealthCheckView")


class TestGetUrlDetail(UrlsPanelTestCase):
    def test_missing_name_pattern_and_view_fails(self):
        result = handle_get_url_detail(_ctx())
        self.assertFalse(result.success)

    def test_unknown_name_fails(self):
        result = handle_get_url_detail(_ctx(name="no:such-url"))
        self.assertFalse(result.success)

    def test_unknown_pattern_fails(self):
        result = handle_get_url_detail(_ctx(pattern="/no/such/url/"))
        self.assertFalse(result.success)

    def test_unknown_view_fails(self):
        result = handle_get_url_detail(_ctx(view="NoSuchViewXyz"))
        self.assertFalse(result.success)

    def test_lookup_by_name(self):
        result = handle_get_url_detail(_ctx(name=HEALTH_NAME))
        self.assertTrue(result.success)
        self.assertEqual(len(result.data["urls"]), 1)
        self.assertEqual(result.data["urls"][0]["pattern"], HEALTH_PATTERN)

    def test_lookup_by_pattern(self):
        result = handle_get_url_detail(_ctx(pattern=HEALTH_PATTERN))
        self.assertTrue(result.success)
        self.assertEqual(result.data["urls"][0]["name"], HEALTH_NAME)

    def test_name_takes_priority_over_pattern(self):
        result = handle_get_url_detail(
            _ctx(name=HEALTH_NAME, pattern="/no/such/url/")
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["urls"][0]["name"], HEALTH_NAME)

    def test_name_takes_priority_over_view(self):
        result = handle_get_url_detail(
            _ctx(name=HEALTH_NAME, view="api.views.ArticleViewSet")
        )
        self.assertTrue(result.success)
        self.assertEqual(result.data["urls"][0]["name"], HEALTH_NAME)

    def test_http_methods_populated(self):
        result = handle_get_url_detail(_ctx(name=HEALTH_NAME))
        self.assertIn("GET", result.data["urls"][0]["http_methods"])

    def test_url_parameters_populated_for_detail_route(self):
        result = handle_get_url_detail(_ctx(name="api:generic-article-detail"))
        params = result.data["urls"][0]["url_parameters"]
        self.assertEqual(len(params), 1)
        self.assertEqual(params[0]["name"], "pk")

    def test_serializer_info_present_for_drf_view(self):
        result = handle_get_url_detail(_ctx(name=GENERIC_ARTICLE_LIST_NAME))
        self.assertIsNotNone(result.data["urls"][0]["serializer_info"])

    def test_view_lookup_dotted_path_matches_function_view(self):
        result = handle_get_url_detail(_ctx(view="api.views.article_list"))
        self.assertTrue(result.success)
        names = {u["name"] for u in result.data["urls"]}
        self.assertEqual(names, {FUNC_ARTICLE_LIST_NAME})

    def test_view_lookup_bare_name_matches_class_based_view(self):
        result = handle_get_url_detail(_ctx(view="HealthCheckView"))
        self.assertTrue(result.success)
        names = {u["name"] for u in result.data["urls"]}
        self.assertEqual(names, {HEALTH_NAME})

    def test_view_lookup_matches_every_route_it_backs(self):
        """ArticleViewSet is registered on a router, so several distinct URL
        patterns (list/detail/publish/unpublish/published) all resolve back
        to the same view class."""
        result = handle_get_url_detail(_ctx(view="api.views.ArticleViewSet"))
        self.assertTrue(result.success)
        names = {u["name"] for u in result.data["urls"]}
        self.assertIn("api:article-list", names)
        self.assertIn("api:article-detail", names)
        self.assertIn("api:article-publish", names)
        self.assertGreaterEqual(len(names), 3)
        for url in result.data["urls"]:
            self.assertEqual(url["view_class"], "api.views.ArticleViewSet")

    def test_view_lookup_case_insensitive_match(self):
        result = handle_get_url_detail(_ctx(view="healthcheckview"))
        self.assertTrue(result.success)


class TestInspectView(UrlsPanelTestCase):
    def test_missing_dotted_path_fails(self):
        result = handle_inspect_view(_ctx())
        self.assertFalse(result.success)

    def test_unresolvable_path_fails(self):
        result = handle_inspect_view(_ctx(dotted_path="no.such.module.View"))
        self.assertFalse(result.success)

    def test_no_dot_path_fails(self):
        result = handle_inspect_view(_ctx(dotted_path="lonely"))
        self.assertFalse(result.success)

    def test_resolves_function_view(self):
        """dj_urls_panel.views.index is a plain, undecorated FBV - a cleaner
        fixture than api.views.article_list, whose @api_view decorator
        replaces it with a generic closure (see the dedicated quirk test
        below)."""
        result = handle_inspect_view(_ctx(dotted_path="dj_urls_panel.views.index"))
        self.assertTrue(result.success)
        self.assertEqual(result.data["kind"], "function")
        self.assertEqual(result.data["module"], "dj_urls_panel.views")
        self.assertEqual(result.data["qualname"], "index")

    def test_drf_api_view_function_resolves_to_generic_wrapper(self):
        """Documents a known quirk: resolving the dotted path of a function
        decorated with DRF's @api_view lands on the generic
        `View.as_view.<locals>.view` closure it's replaced by, not the
        original function - so source/qualname aren't meaningful here.
        Use get_url_detail (which reads view_class) to get back to
        'api.views.article_list' instead."""
        result = handle_inspect_view(_ctx(dotted_path="api.views.article_list"))
        self.assertTrue(result.success)
        self.assertEqual(result.data["kind"], "function")
        self.assertEqual(result.data["module"], "api.views")
        self.assertNotEqual(result.data["qualname"], "article_list")

    def test_resolves_class_based_view(self):
        result = handle_inspect_view(_ctx(dotted_path="api.views.HealthCheckView"))
        self.assertTrue(result.success)
        self.assertEqual(result.data["kind"], "class")
        self.assertEqual(result.data["qualname"], "HealthCheckView")

    def test_source_location_populated(self):
        result = handle_inspect_view(_ctx(dotted_path="api.views.HealthCheckView"))
        self.assertTrue(result.data["source_file"].endswith("views.py"))
        self.assertIsInstance(result.data["source_line"], int)

    def test_docstring_captured(self):
        result = handle_inspect_view(_ctx(dotted_path="api.views.HealthCheckView"))
        self.assertIn("health check", result.data["docstring"].lower())

    def test_connected_urls_lists_matching_routes(self):
        result = handle_inspect_view(_ctx(dotted_path="api.views.HealthCheckView"))
        connected = result.data["connected_urls"]
        self.assertEqual(len(connected), 1)
        self.assertEqual(connected[0]["name"], HEALTH_NAME)

    def test_connected_urls_lists_every_route_for_viewset(self):
        result = handle_inspect_view(_ctx(dotted_path="api.views.ArticleViewSet"))
        connected_names = {u["name"] for u in result.data["connected_urls"]}
        self.assertIn("api:article-list", connected_names)
        self.assertIn("api:article-detail", connected_names)

    @override_settings(DJ_URLS_PANEL_SETTINGS={"SHOW_SOURCE": True})
    def test_show_source_true_populates_preview(self):
        result = handle_inspect_view(_ctx(dotted_path="dj_urls_panel.views.index"))
        self.assertIsNotNone(result.data["source_preview"])
        self.assertIn("def index", result.data["source_preview"])

    @override_settings(DJ_URLS_PANEL_SETTINGS={"SHOW_SOURCE": False})
    def test_show_source_false_omits_preview_but_keeps_location(self):
        result = handle_inspect_view(_ctx(dotted_path="dj_urls_panel.views.index"))
        self.assertIsNone(result.data["source_preview"])
        self.assertIsNotNone(result.data["source_file"])
