# Instatiate Django and import settings
import os
import sys

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


def vcf(args, parsers):
    if args.output is None:
        parsers["vcf"].print_help()
        return
    generate_vcf(args.output, args.output_type, args.verbose)


def annot(args, parsers):
    print(args)


if __name__ == "__main__":
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
        description="Annotate positions with mutation name and other info.",
        help="annotate positions with mutation name and other info",
    )
    parsers["annot"].set_defaults(func=annot)

    args = parser.parse_args()
    if "func" in args:
        args.func(args, parsers)
    else:
        parser.print_help()
