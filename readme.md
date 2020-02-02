# tlacli: A CLI tool for TLA+

**DISCLAIMER:** This is not an official TLA+ tool and isn't a prototype for one. I'm not making any guarantees of backwards compatibility or non-breaking changes or whatever. It's just a script I find useful.

`tlacli` is a tool for running the TLC model checker from the command line. You can already run TLC from the command line, anyway, using `tlc2.TLC`, and `tlacli` only provides a subset of the functionality. It still has a few UX improvements, though:

1. Nicer flag UX. Arguments follow the conventional "flag" format. You can spot-check a spec with just `python tlacli.py specfile.tla`. 
1. Saner defaults. It automatically uses `Spec` as your temporal formula, defaults to using a worker per CPU core, gives terse output, etc.
1. You don't have to write a config file. You can define invariants, properties, and constants as command-line flags and `tlacli` will automatically build the proper config file for that run. You can also save the configuration as a template for future runs. You can also use _both_ a config file and flags, where the config is a template and the flags are specializations.

## Setup

You need Java and Python 3.7. There's no package, just clone and run. The `requirements.txt` is only needed for testing. The python script is in `tlacli/tlacli`.

## Using

All examples assume you are in the `tlacli/tlacli` folder.

```
python tlacli.py specfile.tla
```

By default, this runs `specfile.tla` with the specification `Spec`. You can change the run specification with the `--spec` flag. By default, this runs TLC with the `-terse` and `-cleanup` flags. The config file will be saved as `temporary.cfg`. You can change the filename with `--cfg-out {name}`.

**NOTE:** Running currently creates an empty `states` directory.

### Properties

You can specify invariants and properties from the command line. Use the `--invariant {inv}` flag and the `--property {prop}` flag, respectively. Both accept multiple operators.

**NOTE:** If `--invariant` or `--property` are the _last_ flags passed in, the script will assume your specfile is an invariant! You can prevent this by adding a `--`.

```
python tlacli.py --invariant Inv1 Inv2 -- specfile.tla
```

You can also use `--inv` and `--prop`, but this may change in the future.

### Constants

You can assign constants with `--constant {name} {value}`. Each constant must be a separate flag. You can put in sets, tuples, etc by putting `{value}` in quotes. Use single quotes if you want to put in strings.

```
python tlacli.py --constant Max 4 --constant Threads '{1, 2}' specfile.tla
python tlacli.py --constant Colors '{\"red\", \"green\"}' specfile.tla
```

#### Model Values

If you need several model values, you can specify them all in a single `--model-values {m1} {m2} ...` flag.

```
python tlacli.py --model_values A B C Null Server -- specfile.tla
```

#### Sets of Model Values

Use an ordinary assignment. You don't need a `--model-values` flag first.

```
# Wrong
python tlacli.py --model-values m1 m2 m3 --constant ModelSet "{m1, m2, m3}" specfile.tla


# Right
python tlacli.py --constant ModelSet "{m1, m2, m3}" specfile.tla
```

Symmetry sets are not yet supported.

### Configuration Templates

You can specify a template configuration with `--cfg template.cfg`:

```
python tlacli.py --cfg foo.cfg specfile.tla
```

`tlacli` can only read things that are also expressible as flags. Currently, this means invariants, properties, specification, and (most) constants. Everything else is ignored. It's a simple text parser and may miss things formated in an unexpected way. The one guarantee: If you write a file a config with `--cfg-out` and later read it with `--cfg`, the whole config will be read properly.

A template can be used in conjunction with the other flags. Currently this adds the additional flags on top of the template. The plan is that if the flags and the template conflict, the flags take priority. This will let us specialize a template.

**BUG:** Constants are currently additive. That doesn't make sense

## Contributing

Eh make a PR or something

### Testing

TODO

## TODO

### Features
* Translating PlusCal (probably means implementing subparsers)
* Implement and document all the TLC options here: https://lamport.azurewebsites.net/tla/tlc-options.html
* Symmetry model sets
* More post-run cleanup
* Maybe use fewer workers per run
* Advanced config options:
    * VIEW (chaos reigns)
    * Operator Overrides / Constant Operators
    * CONSTRAINT and ACTION-CONSTRAINT
    * SYMMETRY
* Explanations on what you can and can't assign in a config file (anything that doesn't require `EXTENDS`, I think)
* Writing on landmines and stuff
* Add tests
* Make it easier to add to your $PATH

### Internal

* Move config manipulation functions to its own module
* Make a CFG class to simplify everything

## Out of Scope

* INIT-NEXT config
* TLAPS and tla2tex
* Toolbox-only features like profiling, running in the cloud, trace explorer, "evaluate constant expression"
