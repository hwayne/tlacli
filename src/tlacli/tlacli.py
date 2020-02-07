import argparse

from tlacli.tools import tlc, pluscal




parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(help="Which TLA+ tool to run")

tlc.setup(subparsers)
pluscal.setup(subparsers)


def main():
    try:
        args = parser.parse_args()
        args.run(args)
    except AttributeError:
        parser.print_help()
        parser.exit()

if __name__ == "__main__":
    
    """Each TLA+ tool has its own parser, which also handles running the command.
    If you're looking for the model checker, you want tools/tlc.py"""
    main()
