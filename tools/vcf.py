import gzip
import io
import os
import re
import sys

from contextlib import nullcontext

from models.models import YMutations


def _generate_vcf(verbose, file_exc):
    def _unify(content):
        if content == "":
            return "."

        return re.sub(r"\s+", "_", content)

    def _get_record(mutation, name):
        return (
            f"chrY\t{mutation.position}\t{name}\t{mutation.ancestral}\t{mutation.derived}\t100\tPASS\t"
            + f"YCC={_unify(mutation.ycc_haplogroup)};ISOGG={_unify(mutation.isogg_haplogroup)};"
            + f"REF={_unify(mutation.ref)};COMMENT={_unify(mutation.comment)}\n"
        )

    with open(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "../resources/template.vcf"), "rt", encoding="utf_8"
    ) as header_exc:
        header = header_exc.readlines()

    if isinstance(file_exc, io.TextIOWrapper):
        cm = nullcontext(file_exc)
    else:
        cm = io.TextIOWrapper(file_exc, encoding="utf_8")

    with cm as text_file_exc:
        text_file_exc.writelines(header)

        query = (
            YMutations.objects.exclude(name="Root")
            .order_by("position", "ancestral", "derived", "join_date", "name")
            .iterator()
        )

        last_mutation = None
        if verbose:
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

                # record last mutation
                if mutation_name is not None:
                    text_file_exc.write(_get_record(last_mutation, mutation_name))

                mutation_name = mutation.name
                last_mutation = mutation

            text_file_exc.write(_get_record(last_mutation, mutation_name))
        else:
            for mutation in query:
                if (
                    last_mutation is not None
                    and mutation.position == last_mutation.position
                    and mutation.ancestral == last_mutation.ancestral
                    and mutation.derived == last_mutation.derived
                ):
                    continue

                text_file_exc.write(_get_record(mutation, mutation.name))
                last_mutation = mutation


def generate_vcf(output, output_type, verbose):
    # check args first
    if sys.version_info < (3, 7):
        print("ERROR: Please upgrade your Python version to 3.7.0 or higher")
        sys.exit(1)

    if output_type is None and output.name.lower().endswith(".gz") or output_type is not None and output_type == "z":
        if isinstance(output, io.TextIOWrapper):
            print(
                "ERROR: You can't output compressed VCF to STDOUT unless upgrade your Python version to 3.10.3 or higher"
            )
            sys.exit(1)

        cm = gzip.open(output, "wb")
    else:
        cm = nullcontext(output)

    with cm as file_exc:
        _generate_vcf(verbose, file_exc)
