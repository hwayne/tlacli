## Removals

Both the template and the flags are additive, so there's no way to remove an invariant or property that's already in a template. Originally I had a `no-invariant` flag planned, but I haven't needed it yet so dropped the plan for simplicity. We might need to add it again if we implement views and symmetry sets, but I find it unlikely.

There's no need to remove constants or model values: extra model values do not affect the spec, and all constants must be defined anyway.

## Parsing Output

Right now we're just dumping the output. I'd like to be able to preprocess error traces, so instead of false assertions raising an exception they just print that the assert failed. That would confuse beginners a lot less.

If we parse we should adapt @algyn's fantastic work on the [vscode extension](https://github.com/alygin/vscode-tlaplus). See for example https://github.com/alygin/vscode-tlaplus/blob/master/src/parsers/tlcCodes.ts

java -cp .\tla2tools.jar pcal.trans  