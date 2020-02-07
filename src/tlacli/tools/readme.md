This folder holds all of the command line subparsers. There is one subparser for each implemented TLA+ tool:

* `TLC`
* `PlusCal`

## Design Notes

Each file has (at least) a `setup` and a `run` function. `setup` takes in the main "subparser action", which is the hook for adding distinct subparser. Adding the new subparser is a mutation on the original parser- each `setup` has side effects. They are only called once.All `setup`s should add `run=run` as an additional default. That way, no matter what command we choose, `run` is always available on the main parser. See the penultimate example [here](https://docs.python.org/3/library/argparse.html#argparse.ArgumentParser.add_subparsers).

All of the `setup`s should define `--show-script` for debuggin purposes. We can't define this in the main parser because then the flag is required before the subparser command, eg we'd have to write

```
tlacli --show-script check ...
```

Instead of the more reasonable `tlacli check --show-script`.

`run` is actually responsible for handling all the logic. That's constructing CFG files, passing in flags to tla2tools, etc. 
