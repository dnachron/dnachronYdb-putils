from collections import defaultdict
import csv
import os
from functools import partial

import pyliftover

from django.utils.functional import SimpleLazyObject

from .constant import OVER_CHAIN_MAP, ReferencesBuilds


def _fill_converter(converter: dict, lazy=True):
    current_folder = os.path.dirname(os.path.abspath(__file__))
    for (left, right), relative_path in OVER_CHAIN_MAP.items():
        if lazy:
            converter[left][right] = SimpleLazyObject(
                partial(pyliftover.LiftOver, os.path.join(current_folder, relative_path), use_web=False)
            )
        else:
            converter[left][right] = pyliftover.LiftOver(os.path.join(current_folder, relative_path), use_web=False)


class CoordinateCoverter:

    _converter = defaultdict(dict)
    _fill_converter(_converter, True)

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
    def __init__(self, input_file, output_file, source_build, target_build, hide_header) -> None:
        if not CoordinateCoverter.check(source_build, target_build):
            raise ValueError(f"not support this convention: {source_build.name} -> {target_build.name}")
        self._converter = partial(CoordinateCoverter.convert, source_build, target_build)
        self._source_build = source_build.name
        self._target_build = target_build.name

        self._csv_reader = csv.reader(input_file)
        self._csv_writer = csv.writer(output_file)
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
