from dj_control_room_base.core import PanelConfig

from .tools import registry as tool_registry

panel_config = PanelConfig(
    settings_key="DJ_URLS_PANEL_SETTINGS",
    defaults={
        "URL_CONFIG": None,
        "EXCLUDE_URLS": [],
        "ENABLE_TESTING": True,
        "ALLOWED_HOSTS": None,
        "SHOW_SOURCE": False,
    },
    tools=tool_registry.tools,
)
