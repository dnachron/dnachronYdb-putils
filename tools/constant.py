from enum import Enum, auto
from types import DynamicClassAttribute


HEADER = ["POS", "REF", "ALT", "NORM_POS", "NORM_REF", "NORM_ALT", "ID", "YCC", "ISOGG", "reference", "comment"]


class ReferencesBuilds(Enum):
    HG19 = auto()
    HG38 = auto()
    CP086569_1 = auto()
    CP086569_2 = auto()

    @DynamicClassAttribute
    def name(self):
        name = super().name
        return name.replace("_", ".")


DATABASE_BUILD = ReferencesBuilds.HG38
