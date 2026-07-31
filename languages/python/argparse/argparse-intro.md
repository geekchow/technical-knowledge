# argparse

The argparse module makes it easy to write user-friendly command-line interfaces. The program defines what arguments it requires, and argparse will figure out how to parse those out of sys.argv. The argparse module also automatically generates help and usage messages. The module will also issue errors when users give the program invalid arguments.


## Positional & Optional params

```python
from argparse import ArgumentParser, Namespace

argparser = ArgumentParser(description="It's a sample cli.")

# positional arg: square, for positional param, the sequence matters.
argparser.add_argument("square", type=int, help="square of a int")

# for optional param you could place it anywhere or even without it.
# the action store_true means when the param presents, give a boolean value: `true` to the param.
argparser.add_argument("-v", "--verbose", help="verose output", action="store_true")

# parse the params into Namespace 
params: Namespace = argparser.parse_args()

if params.verbose:
  print(f"square of {params.square} is {params.square ** 2}")
else:  
  print(params.square ** 2)
```

Input and output 

```shell
# require param is not provided
python3 argparse/01-positional-optional-params.py            

usage: 01-positional-optional-params.py [-h] [-v] square
01-positional-optional-params.py: error: the following arguments are required: square

# get help
python3 argparse/01-positional-optional-params.py -h
usage: 01-positional-optional-params.py [-h] [-v] square

It is a sample cli.

positional arguments:
  square         square of a int

options:
  -h, --help     show this help message and exit
  -v, --verbose  verose output

# param type is wrong
python3 argparse/01-positional-optional-params.py i 
usage: 01-positional-optional-params.py [-h] [-v] square
01-positional-optional-params.py: error: argument square: invalid int value: 'i'

# calc square value with verbose output
python3 argparse/01-positional-optional-params.py 5 --verbose
square of 5 is 25
```


## multiple values param

```python
from argparse import Namespace, ArgumentParser

argparser = ArgumentParser(description="Sum or Max input values")

# a multiple values param integers
# nargs="+": Number of times the argument can be used (int, '?', '*', or '+')
# metavar="N": Alternate display name for the argument as shown in help
argparser.add_argument("integers", metavar="N", type=int, nargs="+", help="an integer for accumulator")

# dest="accumulate": the key in arg namespace
# action="store_const": going to take the param: const=max (max is a python built-in function)
# default=max: the default value is max
# const=sum: when --sum present, the param values is sum
argparser.add_argument("--sum", dest="accumulate", action="store_const", default=max, const=sum, help="sum the integers (default: get the max)")

params: Namespace = argparser.parse_args()

print(params)

print(params.accumulate(params.integers))
    
```

input and output
```shell
# sum doesn't present, so do default operation: max
python3 argparse/02-multiple-values-param.py 1 3 4
Namespace(integers=[1, 3, 4], accumulate=<built-in function max>)
4

# specify --sum. so do sum operation
python3 argparse/02-multiple-values-param.py 1 3 4 --sum  
Namespace(integers=[1, 3, 4], accumulate=<built-in function sum>)
8

# get help 
python3 argparse/02-multiple-values-param.py -h
usage: 02-multiple-values-param.py [-h] [--sum] N [N ...]

Sum or Max input values

positional arguments:
  N           an integer for accumulator

options:
  -h, --help  show this help message and exit
  --sum       sum the integers (default: get the max)

# parse params directly
parser.parse_args(['--sum', '7', '-1', '42'])
Namespace(accumulate=<built-in function sum>, integers=[7, -1, 42])
```


## sub command

```python
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

print(parser.parse_args(['--help']))

print(arser.parse_args(['a', '--help']))

print(parser.parse_args(['b', '--help']))
```