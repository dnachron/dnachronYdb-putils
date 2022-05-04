from enum import Enum, auto


HEADER = ["POS", "REF", "ALT", "NORM_POS", "NORM_REF", "NORM_ALT", "ID", "YCC", "ISOGG", "reference", "comment"]


class ReferencesBuilds(Enum):
    HG19 = auto()
    HG38 = auto()
    CP086569_1 = auto()
    CP086569_2 = auto()
