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