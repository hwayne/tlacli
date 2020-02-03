import argparse

import tools.tlc as tlc




parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="Which TLA+ tool to run")

tlc.setup(subparsers)

if __name__ == "__main__":
    
    """Each TLA+ tool has its own parser, which also handles running the command.
    If you're looking for the model checker, you want tools/tlc.py"""
    args = parser.parse_args()
    args.run(args)


    # `java -cp .\tla2tools.jar pcal.trans  `
