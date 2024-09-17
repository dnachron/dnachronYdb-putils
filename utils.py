#!/usr/bin/env python3
# ruff: noqa: E402
import os
import sys

# check before start django
if not (
    os.path.exists(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "dnachronYdb/dnachronYdb.sqlite3",
        )
    )
    or os.path.exists(
        os.path.join(
            os.path.dirname(os.path.realpath(__file__)), "ymutations/ymutations.sqlite3"
        )
    )
):
    print(
        "Can't find the database file dnachronYdb/dnachronYdb.sqlite3 or ymutations/ymutations.sqlite3."
    )
    sys.exit(1)

# mark django settings module as settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# instantiate a web sv for django which is a wsgi
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# self program start here
import argparse

from settings import DATABASE_BUILD

from tools.vcf import generate_vcf
from tools.annotate import AnnotateMutation
from tools.lift import CoordinateCoverter, LiftOverPositions
from tools.transfer import TransferMutation
from tools.constant import ReferencesBuilds


def convert_build(build):
    if build.lower() in (ReferencesBuilds.T2T.name.lower(), ReferencesBuilds.HS1.name.lower()):
        return ReferencesBuilds.CP086569_2

    for reference_build in ReferencesBuilds:
        if build == reference_build.name.lower():
            return reference_build

    raise ValueError(f"not supported build {build}")


def vcf(args, sub_parsers):
    if args.output is None:
        sub_parsers["vcf"].print_help()
        return
    generate_vcf(args.output, args.output_type, args.verbose)


def annot(args, sub_parsers):
    if args.input is None:
        sub_parsers["annot"].print_help()
        return

    mutation_annotate = AnnotateMutation(
        args.input,
        args.output,
        args.reference,
        convert_build(args.build),
        args.verbose,
        args.appendix,
        args.hide_header,
    )
    mutation_annotate.annotate()


def lift(args, sub_parsers):
    if args.list:
        CoordinateCoverter.list()

    if args.input is None or args.source_build is None or args.target_build is None:
        if not args.list:
            sub_parsers["lift"].print_help()
        return

    lift_over = LiftOverPositions(
        args.input,
        args.output,
        convert_build(args.source_build),
        convert_build(args.target_build),
        args.hide_header,
    )
    lift_over.lift_over()


def trans(args, sub_parsers):
    if args.input is None:
        sub_parsers["trans"].print_help()
        return

    mutation_transfer = TransferMutation(
        args.input,
        args.output,
        convert_build(args.build),
        args.hide_header,
        args.hide_db_pos,
        args.hide_real_name,
    )
    mutation_transfer.transfer()


if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("ERROR: Please upgrade your Python version to 3.7.0 or higher")
        sys.exit(1)

    parser = argparse.ArgumentParser()
    parser.description = "A tool for Y-DNA mutation annotation and liftover. With this tool, you can use t2t or hs1 as aliases for CP086569.2."
    subparsers = parser.add_subparsers()
    parsers = {}

    # create the parser for the "vcf" command
    parsers["vcf"] = subparsers.add_parser(
        "vcf",
        description="Generate mutation vcf file for common bio-tools use. \
            E.g., you can annotate the name to your vcf with this vcf by bcftools annotate directly.",
        help="generate mutation vcf file for common bio-tools use",
    )
    parsers["vcf"].add_argument(
        "output",
        type=argparse.FileType("wb"),
        nargs="?",
        help="the output file, you can output to STDOUT by -",
    )
    parsers["vcf"].add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="include all duplicated names, otherwise only the first name",
    )
    parsers["vcf"].add_argument(
        "-O",
        "--output-type",
        type=str,
        choices="vz",
        help="v/z: un/compressed VCF, \
        if not specified, it will be detected automatically by output file name, or u if can't",
    )
    parsers["vcf"].set_defaults(func=vcf)

    # create the parser for the "annot" command
    parsers["annot"] = subparsers.add_parser(
        "annot",
        description="Annotate positions with mutation name and other info. \
            The input should be a list of mutations: position, ancestral, derived, seprated by comma, and each mutation one line. \
                Or simply use csv format file. You can test with hg19_mutation.csv and hg38_mutation.csv in testdata. \
                    Duplicated mutations will be removed.",
        help="annotate positions with mutation name and other info",
    )
    parsers["annot"].add_argument(
        "input",
        type=argparse.FileType("rt"),
        nargs="?",
        help="the input file, you can input from STDIN by -",
    )
    parsers["annot"].add_argument(
        "-o",
        "--output",
        type=argparse.FileType("wt"),
        nargs="?",
        default="-",
        help="the output file, default to STDOUT if not specified",
    )
    parsers["annot"].add_argument(
        "-b",
        "--build",
        type=str.lower,
        choices=[build.name.lower() for build in ReferencesBuilds],
        default=DATABASE_BUILD.name.lower(),
        help=f"the reference build, default is {DATABASE_BUILD.name.lower()}",
    )
    parsers["annot"].add_argument(
        "-r",
        "--reference",
        type=str,
        nargs="?",
        help=f"if you provide {DATABASE_BUILD.name} reference file, it can try to normalize INDELs before annotate",
    )
    parsers["annot"].add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="include all duplicated names, otherwise only the first name",
    )
    parsers["annot"].add_argument(
        "-a", "--appendix", action="store_true", help="annotate appendix info"
    )
    parsers["annot"].add_argument(
        "-H", "--hide_header", action="store_true", help="don't output header"
    )

    parsers["annot"].set_defaults(func=annot)

    # create the parser for the "trans" command
    parsers["trans"] = subparsers.add_parser(
        "trans",
        description="Transfer mutation name to position, ancestral, derived. \
            The input should be a list of mutation names, each name one line. \
                Or simply use csv format file. You can test with testdata/names.csv. \
                    Duplicated names will be removed.",
        help="transfer mutation name to position, ancestral, derived",
    )
    parsers["trans"].add_argument(
        "input",
        type=argparse.FileType("rt"),
        nargs="?",
        help="the input file, you can input from STDIN by -",
    )
    parsers["trans"].add_argument(
        "-o",
        "--output",
        type=argparse.FileType("wt"),
        nargs="?",
        default="-",
        help="the output file, default to STDOUT if not specified",
    )
    parsers["trans"].add_argument(
        "-b",
        "--build",
        type=str.lower,
        choices=[build.name.lower() for build in ReferencesBuilds],
        default=DATABASE_BUILD.name.lower(),
        help=f"the reference build, default is {DATABASE_BUILD.name.lower()}",
    )
    parsers["trans"].add_argument(
        "-H", "--hide_header", action="store_true", help="don't output header"
    )
    parsers["trans"].add_argument(
        "-B",
        "--hide_db_pos",
        action="store_true",
        help=f"don't output {DATABASE_BUILD.name} position if build is not {DATABASE_BUILD.name}",
    )
    parsers["trans"].add_argument(
        "-N",
        "--hide_real_name",
        action="store_true",
        help="don't output real name in database",
    )

    parsers["trans"].set_defaults(func=trans)

    # create the parser for the "lift" command
    parsers["lift"] = subparsers.add_parser(
        "lift",
        description="Lift over positions between different reference builds. \
            The input should be a list of positions, each position one line. And ignore extra columns.\
                You can test with hg19_mutation.csv and hg38_mutation.csv in testdata. Duplicated positions will be removed.",
        help="lift over positions between different reference builds",
    )
    parsers["lift"].add_argument(
        "-l", "--list", action="store_true", help="list all support lift over builds"
    )
    parsers["lift"].add_argument(
        "input",
        type=argparse.FileType("rt"),
        nargs="?",
        help="the input file, you can input from STDIN by -",
    )
    parsers["lift"].add_argument(
        "-s",
        "--source_build",
        choices=[build.name.lower() for build in ReferencesBuilds],
        type=str.lower,
        help="the souce reference build",
    )
    parsers["lift"].add_argument(
        "-t",
        "--target_build",
        choices=[build.name.lower() for build in ReferencesBuilds],
        type=str.lower,
        help="the target reference build",
    )
    parsers["lift"].add_argument(
        "-o",
        "--output",
        type=argparse.FileType("wt"),
        nargs="?",
        default="-",
        help="the output file, default to STDOUT if not specified",
    )
    parsers["lift"].add_argument(
        "-H", "--hide_header", action="store_true", help="don't output header"
    )
    parsers["lift"].set_defaults(func=lift)

    args = parser.parse_args()
    if "func" in args:
        args.func(args, parsers)
    else:
        parser.print_help()
