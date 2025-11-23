from litestar.openapi.config import OpenAPIConfig
from litestar.openapi.plugins import ScalarRenderPlugin

from app.config.settings import get_settings


settings = get_settings()

config = OpenAPIConfig(
    title=settings.app.NAME,
    version=settings.app.VERSION,
    # components=[],
    # security=[],
    use_handler_docstrings=True,
    render_plugins=[ScalarRenderPlugin()],
    path="/docs"
)
