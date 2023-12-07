from core.common import parse_args, ArgsError
from cli import run_cli
from gui import run_gui

if __name__ == '__main__':
    args, parser = parse_args()
    try:
        if args.batch:
            run_cli(args)
        else:
            run_gui(args)
    except ArgsError as e:
        parser.error(e.message)
