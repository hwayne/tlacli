This folder holds all of the command line subparsers. There is one subparser for each implemented TLA+ tool:

* `TLC`


## Design Notes

Each file has (at least) a `setup` and a `run` function. `setup` takes in the main "subparser action", which is the hook for adding distinct subparser. Adding the new subparser is a mutation on the original parser- each `setup` has side effects. They are only called once.All `setup`s should add `run=run` as an additional default. That way, no matter what command we choose, `run` is always available on the main parser. See the penultimate example [here](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers).

`run` is actually responsible for handling all the logic. That's constructing CFG files, passing in flags to tla2tools, etc. 
