import csv
from operator import itemgetter

from pyfaidx import Fasta

from models.models import YMutations
from tools.lift import CoordinateCoverter

from .constant import DATABASE_BUILD, HEADER


def _trim_mutation(mutation, ancestral, ancestral_len, derived, derived_len):
    """
    doesn't check common from left to right
    """
    if ancestral_len > derived_len and ancestral[1 + ancestral_len - derived_len :] == derived[1:]:
        return (mutation[0], ancestral[: -derived_len + 1], derived[: -derived_len + 1])

    if ancestral_len < derived_len and ancestral[1:] == derived[1 + derived_len - ancestral_len :]:
        return (mutation[0], ancestral[: -ancestral_len + 1], derived[: -ancestral_len + 1])

    return None


def _trim_same_len(mutation, ancestral, ancestral_len, derived):
    offset = 0
    if ancestral_len > 1:
        while ancestral[-1] == derived[-1]:
            ancestral = ancestral[:-1]
            derived = derived[:-1]
        while ancestral[0] == derived[0]:
            ancestral = ancestral[1:]
            derived = derived[1:]
            offset += 1

        # don't support MNP and complex
        if len(ancestral) > 1:
            return None

    # don't check SNP
    return (mutation[0] + offset, ancestral, derived)


def mutation_normalize(mutation, genes, with_out_check_ref=False):
    """
    mutation: (position, ancestral, derived)
    when with_out_check_ref = True, genes could be None.
    position shuld be int
    """
    if genes is None and not with_out_check_ref:
        raise ValueError("genes can't be None if not with_out_check_ref")

    ancestral = mutation[1]
    derived = mutation[2]
    if derived == "*":
        return None

    ancestral_len = len(ancestral)
    derived_len = len(derived)

    # accept max length 100
    if ancestral_len > 99:
        ancestral = ancestral[0:99]
        ancestral_len = 99
    if derived_len > 99:
        derived = derived[0:99]
        derived_len = 99

    if mutation[1] == mutation[2]:
        return None

    if ancestral_len == derived_len:
        return _trim_same_len(mutation, ancestral, ancestral_len, derived)

    if not with_out_check_ref:
        seq = str(genes["chrY"][mutation[0] - 1 : mutation[0] + ancestral_len - 1]).upper()
        if seq != ancestral:
            # check if ancestral same with ref
            return None

        seq = str(genes["chrY"][mutation[0] - 251 : mutation[0] - 1]).upper()

        if ancestral_len > derived_len:
            ancestral_seq = seq[ancestral_len - derived_len :] + ancestral
            derived_seq = seq + derived
        elif ancestral_len < derived_len:
            ancestral_seq = seq + ancestral
            derived_seq = seq[derived_len - ancestral_len :] + derived
        else:
            # don't support mnp and complex
            return None

        for i in range(0, 250):
            if ancestral_seq[250 - i] != derived_seq[250 - i]:
                break

        if i > 0:
            ancestral = ancestral_seq[-i - ancestral_len : -i]
            derived = derived_seq[-i - derived_len : -i]
            mutation = (mutation[0] - i, mutation[1], mutation[2])

    # left different, maybe mnp or complex, we don't support
    if ancestral[0] != derived[0]:
        return None

    # check trim
    if ancestral_len != 1 and derived_len != 1:
        return _trim_mutation(mutation, ancestral, ancestral_len, derived, derived_len)

    # after trim, add
    return (mutation[0], ancestral, derived)


class AnnotateMutation:
    def __init__(self, input, output, reference, build, verbose, appendix, hide_header) -> None:
        self._csv_reader = csv.reader(input)
        self._csv_writer = csv.writer(output)
        if reference is not None:
            self._genes = Fasta(reference, rebuild=False)
        else:
            self._genes = None
        self._build = build
        self._verbose = verbose
        self._appendix = appendix
        self._hide_header = hide_header
        self._mutations = {}

    def _record_mutation(self, mutation, mutation_name):
        key = (mutation.position, mutation.ancestral, mutation.derived)
        if key in self._mutations:
            if self._appendix:
                self._mutations[key].extend(
                    [
                        mutation_name,
                        mutation.ycc_haplogroup,
                        mutation.isogg_haplogroup,
                        mutation.ref,
                        mutation.comment,
                    ]
                )
            else:
                self._mutations[key].append(mutation_name)

    def _add_mutation(self, row):
        position = int(row[0])
        if self._build != DATABASE_BUILD:
            new_position = CoordinateCoverter.convert(self._build, DATABASE_BUILD, int(row[0]))

            if new_position is None:
                # make the position different from any reference builds
                self._mutations[(position + 80000000, row[1], row[2])] = [row[0], row[1], row[2]]
                return
            position = new_position

        ori_mutation = (position, row[1].upper(), row[2].upper())
        mutation = None
        if self._genes is not None:
            mutation = mutation_normalize(ori_mutation, self._genes)

        # check without ref if needed
        if mutation is None:
            mutation = mutation_normalize(ori_mutation, self._genes, with_out_check_ref=True)

        # if can't pass any detect, only use the ori_mutation
        if mutation is None:
            mutation = ori_mutation

        self._mutations[mutation] = [row[0], row[1], row[2], *mutation]

    def annotate(self):
        stoped = False
        try:
            header = next(self._csv_reader)
        except StopIteration:
            stoped = True

        if header[0].isdigit():
            self._add_mutation(header)
            header = None

        while not stoped:
            try:
                row = next(self._csv_reader)
                self._add_mutation(row)
            except StopIteration:
                stoped = True

        if not self._hide_header:
            if header is not None:
                header = header[:3]
                if self._appendix:
                    header.extend(HEADER[3:])
                else:
                    header.extend(HEADER[3:7])
            else:
                if self._appendix:
                    header = HEADER
                else:
                    header = HEADER[:7]
            self._csv_writer.writerow(header)

        query = (
            YMutations.objects.filter(position__in=map(itemgetter(0), self._mutations.keys()))
            .order_by("position", "ancestral", "derived", "join_date", "name")
            .iterator()
        )

        last_mutation = None
        if self._verbose:
            mutation_name = None
            for mutation in query:
                if (
                    last_mutation is not None
                    and mutation.position == last_mutation.position
                    and mutation.ancestral == last_mutation.ancestral
                    and mutation.derived == last_mutation.derived
                ):
                    mutation_name = mutation_name + "/" + mutation.name
                    continue

                if mutation_name is not None:
                    self._record_mutation(last_mutation, mutation_name)

                mutation_name = mutation.name
                last_mutation = mutation

            self._record_mutation(last_mutation, mutation_name)
        else:
            for mutation in query:
                if (
                    last_mutation is not None
                    and mutation.position == last_mutation.position
                    and mutation.ancestral == last_mutation.ancestral
                    and mutation.derived == last_mutation.derived
                ):
                    continue

                self._record_mutation(mutation, mutation.name)
                last_mutation = mutation

        self._csv_writer.writerows(self._mutations.values())
