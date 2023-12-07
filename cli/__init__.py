import os
import argparse

from cli.cli_app import run_aseprite, run_blender
from core.common import parse_args, ArgsError


def run_cli(args: argparse.Namespace):
    if args.batch and (args.input is None or args.output is None):
        raise ArgsError('--batch requires --input and --output')

    if not os.path.isfile(args.input):
        raise ArgsError(f'Input is not a file: {args.input}')

    if args.create_output_dir:
        os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output):
        raise ArgsError(f'Output is not a directory: {args.output}')

    run_aseprite(args)
    if not args.svg_only:
        run_blender(args)


if __name__ == '__main__':
    args, parser = parse_args()
    try:
        run_cli(args)
    except ArgsError as e:
        parser.error(e.message)
