from enum import Enum, auto
from types import DynamicClassAttribute


HEADER = ["POS", "REF", "ALT", "NORM_POS", "NORM_REF", "NORM_ALT", "ID", "YCC", "ISOGG", "reference", "comment", "Ybrowse_Synced"]


class ReferencesBuilds(Enum):
    """
    The build name's "_" character will be replaced by "."
    """

    HG19 = auto()
    HG38 = auto()
    CP086569_1 = auto()
    CP086569_2 = auto()
    T2T = auto()
    HS1 = auto()

    @DynamicClassAttribute
    def name(self):  # pylint: disable=function-redefined
        name = super().name
        return name.replace("_", ".")


OVER_CHAIN_MAP = {
    (ReferencesBuilds.HG19, ReferencesBuilds.HG38): "../resources/hg19ToHg38.over.chain.gz",
    (ReferencesBuilds.HG38, ReferencesBuilds.HG19): "../resources/hg38ToHg19.over.chain.gz",
    (ReferencesBuilds.HG38, ReferencesBuilds.CP086569_1): "../resources/hg38_chrYTocp086569_1.over.chain.gz",
    (ReferencesBuilds.CP086569_1, ReferencesBuilds.HG38): "../resources/cp086569_1Tohg38_chrY.over.chain.gz",
    (ReferencesBuilds.HG19, ReferencesBuilds.CP086569_2): "../resources/hg19Tocp086569_2.over.chain.gz",
    (ReferencesBuilds.CP086569_2, ReferencesBuilds.HG19): "../resources/cp086569_2Tohg19.over.chain.gz",
    (ReferencesBuilds.HG38, ReferencesBuilds.CP086569_2): "../resources/hg38_chrYTocp086569_2.over.chain.gz",
    (ReferencesBuilds.CP086569_2, ReferencesBuilds.HG38): "../resources/cp086569_2Tohg38_chrY.over.chain.gz",
    (ReferencesBuilds.CP086569_2, ReferencesBuilds.CP086569_1): "../resources/cp086569_2Tocp086569_1.over.chain.gz",
    (ReferencesBuilds.CP086569_1, ReferencesBuilds.CP086569_2): "../resources/cp086569_1Tocp086569_2.over.chain.gz",
}


