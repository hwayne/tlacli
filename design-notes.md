## Removals

Both the template and the flags are additive, so there's no way to remove an invariant or property that's already in a template. Originally I had a `no-invariant` flag planned, but I haven't needed it yet so dropped the plan for simplicity. We might need to add it again if we implement views and symmetry sets, but I find it unlikely.

There's no need to remove constants or model values: extra model values do not affect the spec, and all constants must be defined anyway.

(20-2-9 One case where you'd want `--no-properties` is if you have state constraints or are using simulation mode. In that case you shouldn't be able to use a template if it has a liveness check. But maybe you should be making a template without one and adding the prop, instead of making a template with one and removing it.) 

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


## Shared subcommand parsers

There are several TLC flags that only make sense if you pass in `-simulate`. Also, you can't check liveness properties in simulations. So it makes sense to turn simulations into a separate subcommand of tlacli, so we'd write `tlacli simulate --seed=1 file.tla`. But simulation mode still uses a lot of similar options and would benefit from the cfg flags. This means making `cfg_args` a shared module with its own setup that adds the cfg argument group.

Also we should rename `tools` to `subcommands`. There won't be a 1-1 mapping between subcommands and tools anymore. Also also we should rename the files `check` and `translate`, not `tlc` and `pluscal`, and put it in the readme what they correspond to.