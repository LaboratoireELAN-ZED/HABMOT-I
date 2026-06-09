from enum import Enum, auto
from typing import Any


class AnalysesType(Enum):
    pass


class Analysis:
    def __init__(self):
        self.current: dict[AnalysesType, Any] = {}
