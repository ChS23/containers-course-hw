from typing import Optional

import msgspec
from app.lib.schema import CamelizedBaseStruct


class YooKassaEvent(CamelizedBaseStruct):
    object: dict
