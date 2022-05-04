import csv

from django.db.models.functions import Lower

from models.models import YMutations
from tools.lift import CoordinateCoverter

from .constant import DATABASE_BUILD, HEADER


class TransferMutation:
    def __init__(self, input, output, build, hide_header, hide_hg38, hide_real_name) -> None:
        self._csv_reader = csv.reader(input)
        self._csv_writer = csv.writer(output)
        self._build = build
        self._hide_header = hide_header
        self._hide_hg38 = hide_hg38
        self._hide_real_name = hide_real_name
        self._mutations = {}

    def _add_mutation(self, row):
        # here is case insensitive. If there are two names that only case differnt,
        # but refer to different mutations, it can't distinguish them.
        # Maybe no such kind of mutation.
        self._mutations[row[0].lower()] = [
            row[0],
        ]

    def transfer(self):
        stoped = False
        try:
            header = next(self._csv_reader)
        except StopIteration:
            stoped = True

        mutation = YMutations.objects.filter(name=header[0]).first()
        if mutation is not None:
            self._add_mutation(header)
            header = None

        while not stoped:
            try:
                row = next(self._csv_reader)
                self._add_mutation(row)
            except StopIteration:
                stoped = True

        if not self._hide_header:
            header_row = []
            if header is None:
                header_row.append(f"ORI_{HEADER[6]}")
            else:
                header_row.append(header[0])

            if not self._hide_real_name:
                header_row.append(HEADER[6])

            if not self._hide_hg38 and not self._build == DATABASE_BUILD:
                header_row.append(f"{DATABASE_BUILD.name}_POS")

            header_row.append(f"{self._build.name}_POS")
            header_row.extend(HEADER[1:3])

            self._csv_writer.writerow(header_row)

        for mutation in (
            YMutations.objects.annotate(name_lower=Lower("name"))
            .filter(name_lower__in=self._mutations.keys())
            .values_list("name_lower", "name", "position", "ancestral", "derived")
            .iterator()
        ):
            result = []
            if not self._hide_real_name:
                result.append(mutation[1])

            if self._build == DATABASE_BUILD:
                result.append(mutation[2])
            else:
                if not self._hide_hg38:
                    result.append(mutation[2])

                result.append(CoordinateCoverter.convert(DATABASE_BUILD, self._build, mutation[2]))

            result.extend(mutation[3:])
            self._mutations[mutation[0]].extend(result)

        self._csv_writer.writerows(self._mutations.values())
