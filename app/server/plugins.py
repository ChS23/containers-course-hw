from advanced_alchemy.extensions.litestar import SQLAlchemyPlugin
from litestar.plugins.structlog import StructlogPlugin
from litestar_granian import GranianPlugin

from app.config.alchemy import alchemy
from app.config.log import log


structlog = StructlogPlugin(config=log)
alchemy = SQLAlchemyPlugin(config=alchemy)
granian = GranianPlugin()

plugins = [structlog, alchemy, granian]
