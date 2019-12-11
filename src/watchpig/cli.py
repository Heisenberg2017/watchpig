# coding=utf-8

import argparse
import api


WATCH_HELP = """Monitoring document changes.
                Execute relation cmd."""

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(help='cmd')

monitor_parser = subparsers.add_parser(
    'monitor', help=WATCH_HELP, formatter_class=argparse.RawTextHelpFormatter)

monitor_parser.set_defaults(handle=api.multi_watch)

emoji_parser = subparsers.add_parser(
    'emoji', help=WATCH_HELP, formatter_class=argparse.RawTextHelpFormatter)

emoji_parser.set_defaults(handle=api.search_emoji)

emoji_parser.add_argument('--search', '-s', help='search emoji', dest='search', required=True)


def cmd():
    args = parser.parse_args()
    if hasattr(args, 'handle'):
        # print('run args %s' % args.handle)
        args.handle(args)
    else:
        parser.print_help()