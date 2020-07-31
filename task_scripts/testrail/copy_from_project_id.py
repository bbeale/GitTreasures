
from argparse import ArgumentParser, ArgumentError


def main(args):
    """Copy sprints, stories, and/or test cases from one project to another"""
    pass


def parse_args():
    parser = ArgumentParser()
    try:
        parser.add_argument(
            '-f', '--from',
            type=int,
            required=True,
            help='Project ID to copy FROM')
        parser.add_argument(
            '-t', '--to',
            type=int,
            required=True,
            help='Project ID to copy TO')
        parser.add_argument(
            '-s', '--sprints',
            action='store_true',
            required=False,
            help='If true, will copy sprint sections.')
        parser.add_argument(
            '-S', '--stories',
            action='store_true',
            required=False,
            help='If true, copy sprint AND story sections.')
        parser.add_argument(
            '-c', '--cases',
            action='store_true',
            required=False,
            help='If true, copy sprint and story sections + test cases.')
        parser.add_argument(
            '-nc', '--nocases',
            action='store_true',
            required=False,
            help='If true, copy sprint sections + ONLY story sections that have no test cases.'
        )
    except ArgumentError as err:
        raise err
    else:
        return parser.parse_args()


if __name__ == '__main__':
    cli_args = parse_args()
    main(args=cli_args)
