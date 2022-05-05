from collections import defaultdict
import csv
import operator
import os
from functools import partial

import pyliftover

from .constant import OVER_CHAIN_MAP, ReferencesBuilds


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


def _fill_converter(converter: defaultdict(dict)):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    for (left, right), relative_path in OVER_CHAIN_MAP.items():
        converter[left][right] = LazyObject(
            factory=partial(pyliftover.LiftOver, os.path.join(current_folder, relative_path), use_web=False)
        )


class CoordinateCoverter:

    _converter = defaultdict(dict)
    _fill_converter(_converter)

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

    @classmethod
    def list(cls):
        print("supported builds convert:")
        for left, right_dict in cls._converter.items():
            for right in right_dict.keys():
                print(f"{left.name} -> {right.name}")

    @classmethod
    def check(cls, source_build, target_build):
        return source_build in cls._converter and target_build in cls._converter[source_build]


class LiftOverPositions:
    def __init__(self, input, output, source_build, target_build, hide_header) -> None:
        if not CoordinateCoverter.check(source_build, target_build):
            raise ValueError(f"not support this convention: {source_build.name} -> {target_build.name}")
        self._converter = partial(CoordinateCoverter.convert, source_build, target_build)
        self._source_build = source_build.name
        self._target_build = target_build.name

        self._csv_reader = csv.reader(input)
        self._csv_writer = csv.writer(output)
        self._hide_header = hide_header
        self._positions = []

    def _add_position(self, row):
        position = int(row[0])
        new_position = self._converter(position)

        self._positions.append([position, new_position])

    def lift_over(self):
        stoped = False
        try:
            header = next(self._csv_reader)
        except StopIteration:
            stoped = True

        if header[0].isdigit():
            self._add_position(header)
            header = None

        while not stoped:
            try:
                row = next(self._csv_reader)
                self._add_position(row)
            except StopIteration:
                stoped = True

        if not self._hide_header:
            if header is not None:
                header = header[:1]
                header.append(self._target_build)
            else:
                header = [self._source_build, self._target_build]
            self._csv_writer.writerow(header)

        self._csv_writer.writerows(self._positions)
