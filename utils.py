# Instatiate Django and import settings
import os
import sys

from tools.lift import CoordinateCoverter, LiftOverPositions

# check before start django
if not os.path.exists(os.path.join(os.path.dirname(os.path.realpath(__file__)), "dnachronYdb/dnachronYdb.sqlite3")):
    print("Can't find the database file dnachronYdb.sqlite3 at dnachronYdb/dnachronYdb.sqlite3.")
    sys.exit(1)

# mark django settings module as settings.py
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")

# instantiate a web sv for django which is a wsgi
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

# self program start here
import argparse

from tools.vcf import generate_vcf
from tools.annotate import AnnotateMutation
from tools.constant import ReferencesBuilds


def convert_build(build):
    if build == "hg19":
        result = ReferencesBuilds.HG19
    elif build == "hg38":
        result = ReferencesBuilds.HG38
    elif build == "cp086569.1":
        result = ReferencesBuilds.CP086569_1
    elif build == "cp086569.2":
        result = ReferencesBuilds.CP086569_2
    else:
        raise ValueError(f"not supported build {build}")

    return result


def vcf(args, parsers):
    if args.output is None:
        parsers["vcf"].print_help()
        return
    generate_vcf(args.output, args.output_type, args.verbose)


def annot(args, parsers):
    if args.input is None:
        parsers["annot"].print_help()
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


def lift(args, parsers):
    if args.list:
        CoordinateCoverter.list()

    if args.input is None or args.source_build is None or args.target_build is None:
        if not args.list:
            parsers.print_help()
        return

    lift_over = LiftOverPositions(
        args.input, args.output, convert_build(args.source_build), convert_build(args.target_build), args.hide_header
    )
    lift_over.lift_over()


if __name__ == "__main__":
    if sys.version_info < (3, 7):
        print("ERROR: Please upgrade your Python version to 3.7.0 or higher")
        sys.exit(1)

    parser = argparse.ArgumentParser()
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
        "-v", "--verbose", action="store_true", help="include all duplicated names, otherwise only the first name"
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
        choices=["hg19", "hg38", "cp086569.1", "cp086569.2"],
        default="hg38",
        help="the reference build, default is hg38",
    )
    parsers["annot"].add_argument(
        "-r",
        "--reference",
        type=str,
        nargs="?",
        help="if you provide reference file, it can try to normalize INDELs before annotate",
    )
    parsers["annot"].add_argument(
        "-v", "--verbose", action="store_true", help="include all duplicated names, otherwise only the first name"
    )
    parsers["annot"].add_argument("-a", "--appendix", action="store_true", help="annotate appendix info")
    parsers["annot"].add_argument("-H", "--hide_header", action="store_true", help="don't output header")

    parsers["annot"].set_defaults(func=annot)

    # create the parser for the "annot" command
    parsers["lift"] = subparsers.add_parser(
        "lift",
        description="Lift over positions between different reference builds. \
            The input should be a list of positions, each position one line. And ignore extra columns.\
                You can test with testdata/hg19_mutation.csv. Duplicated positions will be removed.",
        help="lift over positions between different reference builds",
    )
    parsers["lift"].add_argument("-l", "--list", action="store_true", help="list all support lift over builds")
    parsers["lift"].add_argument(
        "input",
        type=argparse.FileType("rt"),
        nargs="?",
        help="the input file, you can input from STDIN by -",
    )
    parsers["lift"].add_argument(
        "-s",
        "--source_build",
        choices=["hg19", "hg38", "cp086569.1", "cp086569.2"],
        help="the souce reference build",
    )
    parsers["lift"].add_argument(
        "-t",
        "--target_build",
        choices=["hg19", "hg38", "cp086569.1", "cp086569.2"],
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
    parsers["lift"].add_argument("-H", "--hide_header", action="store_true", help="don't output header")
    parsers["lift"].set_defaults(func=lift)

    args = parser.parse_args()
    if "func" in args:
        args.func(args, parsers)
    else:
        parser.print_help()
