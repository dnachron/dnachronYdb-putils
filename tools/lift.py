from collections import defaultdict
import operator
import os
from functools import partial

import pyliftover

from .constant import ReferencesBuilds


class LazyObject:

    _wrapped = None
    _is_init = False

    def __init__(self, factory):
        # Assign using __dict__ to avoid the setattr method.
        self.__dict__["_factory"] = factory

    def _setup(self):
        self._wrapped = self._factory()
        self._is_init = True

    def new_method_proxy(func):
        """
        Util function to help us route functions
        to the nested object.
        """

        def inner(self, *args):
            if not self._is_init:
                self._setup()
            return func(self._wrapped, *args)

        return inner

    def __setattr__(self, name, value):
        # These are special names that are on the LazyObject.
        # every other attribute should be on the wrapped object.
        if name in {"_is_init", "_wrapped"}:
            self.__dict__[name] = value
        else:
            if not self._is_init:
                self._setup()
            setattr(self._wrapped, name, value)

    def __delattr__(self, name):
        if name == "_wrapped":
            raise TypeError("can't delete _wrapped.")
        if not self._is_init:
            self._setup()
        delattr(self._wrapped, name)

    __getattr__ = new_method_proxy(getattr)
    __bytes__ = new_method_proxy(bytes)
    __str__ = new_method_proxy(str)
    __bool__ = new_method_proxy(bool)
    __dir__ = new_method_proxy(dir)
    __hash__ = new_method_proxy(hash)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __lt__ = new_method_proxy(operator.lt)
    __gt__ = new_method_proxy(operator.gt)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)
    __getitem__ = new_method_proxy(operator.getitem)
    __setitem__ = new_method_proxy(operator.setitem)
    __delitem__ = new_method_proxy(operator.delitem)
    __iter__ = new_method_proxy(iter)
    __len__ = new_method_proxy(len)
    __contains__ = new_method_proxy(operator.contains)


class CoordinateCoverter:
    _converter = defaultdict(dict)
    current_folder = os.path.dirname(os.path.abspath(__file__))
    _converter[ReferencesBuilds.HG19][ReferencesBuilds.HG38] = LazyObject(
        factory=partial(
            pyliftover.LiftOver, os.path.join(current_folder, "../resources/hg19ToHg38.over.chain.gz"), use_web=False
        )
    )
    _converter[ReferencesBuilds.HG38][ReferencesBuilds.HG19] = LazyObject(
        factory=partial(
            pyliftover.LiftOver, os.path.join(current_folder, "../resources/hg38ToHg19.over.chain.gz"), use_web=False
        )
    )
    del current_folder

    @classmethod
    def convert(cls, source: ReferencesBuilds, target: ReferencesBuilds, positions: int):
        try:
            this_converter = cls._converter[source][target]
        except KeyError as exc:
            raise ValueError(f"not support this convention: {source.name} -> {target.name}") from exc

        try:
            return this_converter.convert_coordinate("chrY", positions - 1, "+")[0][1] + 1
        except IndexError:
            return None
