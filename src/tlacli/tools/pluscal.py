import subprocess
import sys
from pkg_resources import resource_filename
from argparse import _SubParsersAction, Namespace
from pathlib import Path

def setup(parser: _SubParsersAction) -> None:
    parser_pluscal = parser.add_parser("translate", help="Translate pluscal into TLA+", aliases=["pc", "pluscal"])
    ...

    parser_pluscal.add_argument("Specfile", help="The specfile.tla")
    parser_pluscal.set_defaults(run=run)

def run(args: Namespace):
    spec_path = Path(args.Specfile)
    jar_path = resource_filename('tlacli', 'tla2tools.jar')

    # Unlike with TLC, there's a lot fewer flags + stuff to parse.
    # If people really want -terminate they can add as a spec header
    # -nocfg is default to minimize side effects
    script = f"java -cp {jar_path} pcal.trans -nocfg {spec_path}"

    result = subprocess.run(script, text=True, capture_output=True, shell=True)

    print(result.stderr)
    print(result.stdout)

    sys.exit(result.returncode)

