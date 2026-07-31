from argparse import Namespace, ArgumentParser

argparser = ArgumentParser(description="Sum or Max input values")

# a multiple values param integers
argparser.add_argument("integers", metavar="N", type=int, nargs="+", help="an integer for accumulator")

# dest="accumulate": the key in arg namespace
# action="store_const": going to take the param: const=max (max is a python built-in function)
# default=max: the default value is max
# const=sum: when --sum present, the param values is sum
argparser.add_argument("--sum", dest="accumulate", action="store_const", default=max, const=sum, help="sum the integers (default: get the max)")

params: Namespace = argparser.parse_args()

print(params)

print(params.accumulate(params.integers))
