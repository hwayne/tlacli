## Removals

Both the template and the flags are additive, so there's no way to remove an invariant or property that's already in a template. Originally I had a `no-invariant` flag planned, but I haven't needed it yet so dropped the plan for simplicity. We might need to add it again if we implement views and symmetry sets, but I find it unlikely.

There's no need to remove constants or model values: extra model values do not affect the spec, and all constants must be defined anyway.

## Parsing Output

Right now we're just dumping the output. I'd like to be able to preprocess error traces, so instead of false assertions raising an exception they just print that the assert failed. That would confuse beginners a lot less.

If we parse we should adapt @algyn's fantastic work on the [vscode extension](https://github.com/alygin/vscode-tlaplus). See for example https://github.com/alygin/vscode-tlaplus/blob/master/src/parsers/tlcCodes.ts

Use the `-tool` flag. Split messages with `@!@!@`. Message numbers indicate what the section actually means. The output looks like

```
@!@!@STARTMSG 2190:0 @!@!@
Finished computing initial states: 8 distinct states generated at 2020-01-30 01:40:34.
@!@!@ENDMSG 2190 @!@!@
@!@!@STARTMSG 2110:1 @!@!@
Invariant TypeInvariant is violated.
@!@!@ENDMSG 2110 @!@!@
@!@!@STARTMSG 2121:1 @!@!@
The behavior up to this point is:
@!@!@ENDMSG 2121 @!@!@
```

Probably want to use `pyparse`, which will be convenient but mean we have to package this as a proper python package (since it has dependencies). Adds complexity. Each message type might have to be parsed differently.

For now we're _only_ parsing output, which means we don't have to worry about "sometimes-significant whitespace" in action conjunctions.

## PlusCal

`java -cp .\tla2tools.jar pcal.trans  `

See command line flags [here](https://lamport.azurewebsites.net/tla/p-manual.pdf). `-nocfg` should be a default. The rest of the flags can be safely ignored for now; most of them aren't critical to implement. Might need a "passthrough" option, same as TLC.

The main challenge here will be using argparse subparsers. I'd want it to default to TLC, and only use pluscal if you pass in `python tlacli.py pluscal file`.

