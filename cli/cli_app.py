import argparse
import os

from core.common import call_aseprite_script, call_blender_script, get_files


def run_aseprite(args: argparse.Namespace):
    kwargs = {
        'file': args.input,
        'output': args.output
    }
    if args.size is not None:
        [tile_width, tile_height] = args.size.split('x')
        kwargs['width'] = tile_width
        kwargs['height'] = tile_height
    call_aseprite_script('scripts/aseprite/convert_to_svg.lua', **kwargs)


def run_blender(args: argparse.Namespace):
    kwargs = {
        '-o': args.output
    }
    if args.scale is not None:
        kwargs['--scale'] = args.scale
    if args.extrude is not None:
        kwargs['--extrude'] = args.extrude
    filename = os.path.basename(args.input)
    files = get_files(args.output, f'{filename}_tile_\\d+_\\d+\\.svg$')
    for file in files:
        call_blender_script('scripts/blender/convert_svg_to_fbx.py',
                            **kwargs, **{'-i': file})
