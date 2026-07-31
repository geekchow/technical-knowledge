from argparse import Namespace, ArgumentParser

argparser = ArgumentParser(prog="Sub Command Sample")

argparser.add_argument("-f", "--foo", action="store_true", help="foo value")

subparser = argparser.add_subparsers(help="sub cmd helper")

subparserA = subparser.add_parser("a", help="sub cmd a")
subparserA.add_argument("bar", type=int, help="bar help")

subparserA = subparser.add_parser("b", help="sub cmd b")
subparserA.add_argument("--baz", choices="XYZ", help="baz help")

print(argparser.parse_args("a 12".split(" ")))
# Namespace(foo=False, bar=12)

print(argparser.parse_args("--foo b --baz X".split(" ")))
# Namespace(foo=True, baz='X')

print(argparser.parse_args(['--help']))

print(argparser.parse_args(['a', '--help']))

print(argparser.parse_args(['b', '--help']))