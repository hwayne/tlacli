import argparse
import os
import re
import subprocess
import sys

from itertools import chain
from copy import deepcopy
from multiprocessing import cpu_count  # For default number of worker threads
from pathlib import Path
from typing import List, TypeVar

T = TypeVar('T')

def unique(l: List[T]) -> List[T]:
    return list(set(l))

def flatten(l: List[List[T]]) -> List[T]:
    return list(chain.from_iterable(l))

def base():
    return {
        "spec": "Spec",
        "invariants": [],
        "properties": [],
        "constants": {},
        "model_values": [],
    }

def extract_cfg(cfg_path: str) -> dict:
    """Parses as TLA+ config file into form we can combine with flags.
    
    This follows an EXTREMELY rigid format. 
    If this script writes a cfg and then reads it, it will get an identical configuration. 
    All other behaviors are undefined."""
    out = base()
    with open(cfg_path) as f:
        cfg = f.readlines()
    for line in cfg:
        line = line.strip()

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
                out["constants"][match[1]] = match[2]

    return out

def flags_to_dict_form(args=None) -> dict:
    """Converts cfg_args from object-record form to dictionary form
    To be compatible with the format we read cfg files into"""
    return {
        "spec": args.spec,
        "invariants": args.invariant,
        "properties": args.property,
        "constants": args.constant,
        "model_values": args.model_values,
    }

def construct_cfg(flag_cfg=None, *, template_cfg=None):
    """This returns the cfg that should be constructed, based on the input template.
    All conflicts resolved in favor of flags."""
    if template_cfg:
        cfg_dict = deepcopy(template_cfg)
    else:
        # TODO I can clean this all WAY up with an "empty config generator"
        cfg_dict = {
            "spec": flag_cfg["spec"],
            "invariants": [],
            "properties": [],
            "constants": {},
            "model_values": [],
            }

    # This doesn't preserve ordering. MVP
    # We actually need to make a set operation for no-inv flags

    cfg_dict["invariants"] += flag_cfg["invariants"]
    cfg_dict["invariants"] = unique(cfg_dict["invariants"])

    cfg_dict["properties"] += flag_cfg["properties"]
    cfg_dict["properties"] = unique(cfg_dict["properties"])

    cfg_dict["constants"].update(flag_cfg["constants"])

    # Maybe model_values should be stored as a dict too
    cfg_dict["model_values"] += flag_cfg["model_values"]
    # TODO filter out no-invariants and no-properties
    return cfg_dict

def format_cfg(cfg_dict):

    out = [f"SPECIFICATION {cfg_dict['spec']}"]
    for inv in cfg_dict["invariants"]:
        out.append(f"INVARIANT {inv}")

    for prop in cfg_dict["properties"]:
        out.append(f"PROPERTY {prop}")

    if cfg_dict["model_values"]:
        out.append("\nCONSTANTS \\* model values")
        for model in cfg_dict["model_values"]:
            out.append(f"  {model} = {model}")


    # TODO should this use <- instead of = ?
    # Would break the regex for reading in cfgs
    if cfg_dict["constants"]:
        out.append(r"CONSTANTS \* regular assignments")
        for constant, value in cfg_dict["constants"].items():
            out.append(f"  {constant} = {value}")
    return "\n".join(out)

parser = argparse.ArgumentParser()
cfg_args = parser.add_argument_group("cfg_args", "Configuration values for the TLA+ spec")
tlc_args = parser.add_argument_group("tlc_args", "Runtime values for the TLC model checker")
# https://lamport.azurewebsites.net/tla/tlc-options.html

cfg_args.add_argument("--spec", "--specification", default="Spec", help="The TLA+ specification operator, defaults to Spec")
cfg_args.add_argument("--cfg", help="A template cfg for default values")

# action=extend is python 3.8 only...
cfg_args.add_argument("--invariant", default=[], action="append", nargs='*', help="Adds argument as model invariant, may be specified multiple times")
cfg_args.add_argument("--property", default=[], action="append", nargs='*', help="Adds argument as model temporal property, may be specified multiple times")


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

if __name__ == "__main__":
    args = parser.parse_args()

    # We need this because we're action=append properties,
    # So get [[a, b], [c]] instead of [a, b, c].
    # action=extend is 3.8 only

    args.property = flatten(args.property)
    args.invariant = flatten(args.invariant)


    # We need constants to be a list of tuples to couple name with value
    
    args.constant = {x: y for x, y in args.constant}
   
    flag_cfg = flags_to_dict_form(args)
    if args.cfg:
        cfg_dict = extract_cfg(args.cfg)
        cfg = construct_cfg(flag_cfg=flag_cfg, template_cfg=cfg_dict)
    else:
        cfg = construct_cfg(flag_cfg=flag_cfg)

    cfg = format_cfg(cfg)
    cfg_file = args.cfg_out

    print(cfg)
 
    # We don't use the temporary module because it closes the file when we're done, and we need to pass a filepath into tlc.
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
    result = subprocess.call(script, shell=True)

    sys.exit(result)
    # Does this create an empty folder even when we cleanup the states?
    # TODO remove temporary if flag enabled
