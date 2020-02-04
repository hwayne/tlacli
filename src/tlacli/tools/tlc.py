from argparse import _SubParsersAction, Namespace
from multiprocessing import cpu_count  # For default number of worker threads
from itertools import chain
from typing import List, TypeVar, Set
from tlacli.cfg import CFG, format_cfg
import re
import os
import subprocess
import sys
from pathlib import Path

T = TypeVar('T')

def flatten(l: List[List[T]]) -> Set[T]:
    return set(chain.from_iterable(l))

def extract_cfg(cfg_path: str) -> CFG:
    """Parses as TLA+ config file into form we can combine with flags.
    
    This follows an EXTREMELY rigid format. 
    If this script writes a cfg and then reads it, it will get an identical configuration. 
    All other behaviors are undefined."""
    out = CFG()
    with open(cfg_path) as f:
        cfg = f.readlines()
    for line in cfg:
        line = line.strip()

        # SPECIFICATION
        match = re.match(r"SPECIFICATION (\w+)", line)
        if match:
            out.spec = match[1]

        # INVARIANT
        match = re.match(r"INVARIANT (\w+)", line)
        if match:
            out.invariants.add(match[1])

        # TEMPORAL PROPERTIES
        match = re.match(r"PROPERTY (\w+)", line)
        if match:
            out.properties.add(match[1])

        # CONSTANTS
        # This regex is imperfect for ordinary assignments
        match = re.match(r"(\S+)\s?=\s?(.+)", line)
        if match:
            if match[1] == match[2]:
                out.model_values.add(match[1])
            else:
                out.constants[match[1]] = match[2]

    return out

def run(args: Namespace):
    # We need this because we're action=append properties,
    # So get [[a, b], [c]] instead of [a, b, c].
    # action=extend is 3.8 only

    args.property = flatten(args.property)
    args.invariant = flatten(args.invariant)
    args.model_values = set(args.model_values)


    
    args.constant = {x: y for x, y in args.constant}
    flag_cfg = CFG( spec=args.spec, properties=args.property, invariants=args.invariant, constants = args.constant, model_values=args.model_values)
    cfg = CFG() # base
   
    # We merge template before flags so flag constants override
    if args.cfg:
        cfg = cfg.merge(extract_cfg(args.cfg))

    cfg = cfg.merge(flag_cfg)
    out = format_cfg(cfg)
    cfg_file = args.cfg_out

 
    # We don't use the temporary module because it closes the file when we're done, and we need to pass a filepath into tlc.
    # BUG: fails if passing in an absolute path (raised)
    with open(cfg_file, 'w') as f:

        f.write(out)

    # Actually run stuff
    spec_path = Path(args.Specfile)
    jar_path = Path(sys.path[0], "tla2tools.jar")

    # At some point I want to start parsing the output. That means adding the -tool flag to the script.
    script = f"java -jar {jar_path} -workers {args.tlc_workers} -config {cfg_file} -terse -cleanup {spec_path}"

    #print(script)

    # text=True means STDOUT not treated as bytestream
    # shell=True means shell expansions (like ~) are handled
    # text and capture_output make it python 3.7 only
    # NOTE: stderr a thing
    result = subprocess.run(script, text=True, capture_output=True, shell=True)

    print(result.stdout)

    sys.exit(result.returncode)
    # Does this create an empty folder even when we cleanup the states?
    # TODO remove temporary if flag enabled
    ...


def setup(parser: _SubParsersAction) -> None:
    parser_tlc = parser.add_parser("check", help="Run the TLC model checker on a TLA+ spec.", aliases=["tlc"])

    cfg_args = parser_tlc.add_argument_group("cfg_args", "Configuration values for the TLA+ spec")
    tlc_args = parser_tlc.add_argument_group("tlc_args", "Runtime values for the TLC model checker")
    # https://lamport.azurewebsites.net/tla/tlc-options.html

    cfg_args.add_argument("--spec", "--specification", default="Spec", help="The TLA+ specification operator, defaults to Spec")
    cfg_args.add_argument("--cfg", help="A template cfg for default values")

    # action=extend is python 3.8 only...
    cfg_args.add_argument("--invariant", default=[], action="append", nargs='*', help="Adds argument as model invariant, may be specified multiple times")
    cfg_args.add_argument("--property", default=[], action="append", nargs='*', help="Adds argument as model temporal property, may be specified multiple times")


    # This needs to be append so we get them in pairs matching constants to their assignments
    # We need constants to be a list of tuples to couple name with value
    cfg_args.add_argument("--constant", default=[], nargs=2, action="append", help='{name} {value}')
    cfg_args.add_argument("--model-values", default=[], nargs='+', help='list of model values')

    # TODO I hate --cfg-out, maybe changed to --out-cfg
    parser_tlc.add_argument("Specfile", help="The specfile.tla")
    parser_tlc.add_argument("--cfg-out", default="temporary.cfg", help="Where to save the cfg file, if you want to reuse it")
    # TODO parser.add_argument("--cfg-del", action="store_true", help="If added, deletes cfg file after model checking is complete")
    # TODO for tlc arguments, use store_true and store_false. Might also want to move the parser config into a separate file because there are a lot

    # Maybe the default should be half the threads?
    tlc_args.add_argument("--tlc-workers", default=cpu_count(), help="The number of worker threads to use (default is number of cpus)")
    #tlc_args.add_argument("--tlc-tool", action="store_true", help="If true, outputs debug information")

    # TODO --tlc-no-defaults
    # TODO automatic TLC passthrough option. Would be a raw string dump

    parser_tlc.set_defaults(run=run)
