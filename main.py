from typing import List
from collections import namedtuple
import configparser
import subprocess
import os
import argparse
import shutil
import re

Config = namedtuple('Config', ['blender', 'aseprite'])
Size = namedtuple('Size', ['width', 'height'])


def aseprite(config: Config, filename: str, output: str, size: Size, script: str) -> None:
    command = [config.aseprite,
               '-b',
               '--script-param', 'file={}'.format(filename),
               '--script-param', 'output={}'.format(output),
               '--script-param', 'width={}'.format(size.width),
               '--script-param', 'height={}'.format(size.height),
               '--script', script]
    ret = subprocess.run(command, capture_output=True, text=True)
    print(ret.args)
    print(ret.stdout)
    print(ret.stderr)
    if ret.returncode:
        raise EnvironmentError


def blender(config: Config, svg_files: List[str], output: str, scale: str, script: str) -> None:
    for file in svg_files:
        command = [config.blender, '-b', '-P', script, '--', '-i', file, '-o', output, '--scale', scale]
        ret = subprocess.run(command, capture_output=True, text=True)
        print(ret.args)
        print(ret.stdout)
        print(ret.stderr)
        if ret.returncode:
            raise EnvironmentError


def load_config() -> Config:
    config = configparser.ConfigParser()
    config.read('config.ini')
    app_blender = config.get('App', 'blender', fallback='blender.exe')
    app_aseprite = config.get('App', 'aseprite', fallback='Aseprite.exe')
    return Config(app_blender, app_aseprite)


def main(args: argparse.Namespace) -> None:
    config = load_config()
    if not shutil.which(config.aseprite):
        print('Aseprite not found: {}'.format(config.aseprite))
        return

    if not shutil.which(config.blender):
        print('Blender not found: {}'.format(config.blender))
        return

    if args.verbose:
        print('Blender: {}'.format(config.blender))
        print('Aseprite: {}'.format(config.aseprite))
        print('Input: {}'.format(args.input))
        print('Output: {}'.format(args.output))

    if not os.path.isfile(args.input):
        print("Input is not file: {}".format(args.input))
        return

    os.makedirs(args.output, exist_ok=True)
    if not os.path.isdir(args.output):
        print("Output is not directory: {}".format(args.output))
        return

    [tile_width, tile_height] = args.size.split('x')
    aseprite(config, args.input, args.output, Size(tile_width, tile_height), 'scripts/aseprite/convert_to_svg.lua')
    svg_files = [os.path.join(args.output, each) for each in os.listdir(args.output) if each.endswith('.svg')]
    blender(config, svg_files, args.output, args.scale, 'scripts/blender/convert_svg_to_fbx.py')


def type_size(astring: str) -> str:
    if not re.match('^\\d+x\\d+$', astring):
        raise ValueError
    return astring


def type_float(astring: str) -> str:
    if not re.match('^\\d+(.\\d+)?$', astring):
        raise ValueError
    return astring


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help='aseprite file', required=True)
    parser.add_argument('-o', '--output', help='output directory', required=True)
    parser.add_argument('-s', '--size', help='size of tile. Default: 32x32', default='32x32', type=type_size)
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('--scale', help="fbx scale. Default: 1000", default='1000', type=type_float)
    args = parser.parse_args()
    main(args)
