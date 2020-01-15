import argparse
import os
import re
import subprocess
import sys
from collections import defaultdict
from itertools import chain
from multiprocessing import cpu_count  # For default number of worker threads
from pathlib import Path
from typing import List, TypeVar

T = TypeVar('T')

# TODO, this seems to fail if you pass in a path. I think you need to be in the same directory or something for tlc to work

def unique(l: List[T]) -> List[T]:
    return list(set(l))

def flatten(l: List[List[T]]) -> List[T]:
    return list(chain.from_iterable(l))

def extract_cfg(cfg_path: str):
    """This current follows an EXTREMELY rigid format. As a rule of thumb, if this script writes a cfg and then reads it, it will get an identical configuration. All other behaviors are undefined."""
    out = defaultdict(list) # So we can append
    with open(cfg_path) as f:
        cfg = f.readlines()
    for line in cfg:
        line = line.strip()
        # Okay, okay, maybe the walrus operator is a good idea.
        # If I stick with extends for argparse might as well use them, since we're stuck on 3.8 anyway then

        # SPECIFICATION
        match = re.match(r"SPECIFICATION (\w+)", line)
        if match:
            out["spec"] = match[1]

        # INVARIANT
        match = re.match(r"INVARIANT (\w+)", line)
        if match:
            out["invariants"].append(match[1])

        # TEMPORAL PROPERTIES
        match = re.match(r"PROPERTY (\w+)", line)
        if match:
            out["properties"].append(match[1])

        # CONSTANTS
        # This regex is imperfect for ordinary assignments
        match = re.match(r"(\S+)\s?=\s?(.+)", line)
        if match:
            if match[1] == match[2]:
                out["model_values"].append(match[1])
            else:
                out["constants"].append((match[1], match[2]))

    return out

def construct_cfg(args=None):
    """This returns the cfg that should be constructed, based on the input template.
    Decisions args"""
    if args.cfg:
        cfg_dict = extract_cfg(args.cfg)
    else:
        cfg_dict = {
            "spec": args.spec,
            "invariants": [],
            "properties": [],
            "constants": [],
            "model_values": [],
            }

    # This doesn't preserve ordering. MVP
    # We use list(set()) to uniquify the list

    cfg_dict["invariants"] += args.invariant
    cfg_dict["invariants"] = unique(cfg_dict["invariants"])

    cfg_dict["properties"] += args.property
    cfg_dict["properties"] = unique(cfg_dict["properties"])

    cfg_dict["constants"] += args.constant
    cfg_dict["constants"] = unique(cfg_dict["constants"])

    # TODO overwrite exising model values from cfg
    # Maybe model_values should be stored as a dict
    cfg_dict["model_values"] += args.model_values
    # TODO filter out no-invariants and no-properties

    out = [f"SPECIFICATION {cfg_dict['spec']}"]
    for inv in cfg_dict["invariants"]:
        out.append(f"INVARIANT {inv}")

    for prop in cfg_dict["properties"]:
        out.append(f"PROPERTY {prop}")

    if cfg_dict["model_values"]:
        out.append("\nCONSTANTS \* model values")
        for model in cfg_dict["model_values"]:
            out.append(f"  {model} = {model}")


    # TODO should this use <- instead of = ?
    # Would break the regex for reading in cfgs
    if cfg_dict["constants"]:
        out.append('CONSTANTS \* regular assignments')
        for constant, value in cfg_dict["constants"]:
            out.append(f"  {constant} = {value}")
    return "\n".join(out)

parser = argparse.ArgumentParser()
cfg_args = parser.add_argument_group("cfg_args", "Configuration values for the TLA+ spec")
tlc_args = parser.add_argument_group("tlc_args", "Runtime values for the TLC model checker")
# https://lamport.azurewebsites.net/tla/tlc-options.html

cfg_args.add_argument("--spec", "--specification", default="Spec", help="The TLA+ specification operator, defaults to Spec")
cfg_args.add_argument("--cfg", help="A template cfg for default values")

# Extend is python 3.8 only...
#cfg_args.add_argument("--invariant", default=[], action="extend", nargs='*', help="Adds argument as model invariant, may be specified multiple times")
#cfg_args.add_argument("--no-invariant", default=[], action="extend", help="Invariants that should NOT be checked")
#cfg_args.add_argument("--property", default=[], action="extend", nargs='*', help="Adds argument as model temporal property, may be specified multiple times")
#cfg_args.add_argument("--no-property", default=[], action="extend", help="Temporal Property that should NOT be checked")

# This needs to be append so we get them in pairs matching constants to their assignments
cfg_args.add_argument("--constant", default=[], nargs=2, action="append", help='{name} {value}')
cfg_args.add_argument("--model-values", default=[], nargs='+', help='list of model values')

parser.add_argument("Specfile", help="The specfile.tla")
parser.add_argument("--cfg-out", default="temporary.cfg", help="Where to save the cfg file, if you want to reuse it")
# TODO parser.add_argument("--cfg-del", action="store_true", help="If added, deletes cfg file after model checking is complete")
# TODO for tlc arguments, use store_true and store_false. Might also want to move the parser config into a separate file because there are a lot

# Maybe the default should be half the threads?
tlc_args.add_argument("--tlc-workers", default=cpu_count(), help="The number of worker threads to use (default is number of cpus)")
tlc_args.add_argument("--tlc-tool", action="store_true", help="If true, outputs debug information")

# TODO --tlc-no-defaults
# TODO automatic TLC passthrough option. Would disable all the other tlc arguments except config

args = parser.parse_args()

# We need constants to be a list of tuples for flattening purposes
# TODO make it a dict
args.constant = [(x, y) for x, y in args.constant]


cfg = construct_cfg(args=args)
# We don't use the temporary module because it closes the file when we're done, and we need to pass a filepath into tlc.
cfg_file = args.cfg_out

print(cfg)
with open(cfg_file, 'w') as f:
    f.write(cfg)

# TLAtools requires the filename to be bare, without path, in the current working directory. If these things are true,
spec_path = Path(args.Specfile)
try:
    if not spec_path.samefile(Path.cwd() / spec_path.name):
        print("Specfile must exist in the current directory.")
        sys.exit(1)
except:
    print("Specfile must exist in the current directory.")
    sys.exit(1)

# Actually run stuff
jar_path = Path(sys.path[0], "tla2tools.jar")
script = f"java -jar {jar_path} -workers {args.tlc_workers} -config {cfg_file} -terse -cleanup {spec_path.name}"
print(script)
#result = subprocess.call(script, shell=True)

sys.exit(result)
# Does this create an empty folder even when we cleanup the states?
# TODO remove temporary if flag enabled
