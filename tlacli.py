import argparse
import subprocess
import sys
from itertools import chain
from collections import defaultdict
import re

# TODO, this seems to fail if you pass in a path. I think you need to be in the same directory or something for tlc to work

def extract_cfg(cfg_path):
    """This current follows an EXTREMELY rigid format. As a rule of thumb, if this script writes a cfg and then reads it, it will get an identical configuration. All other behaviors are undefined."""
    out = defaultdict(list) # So we can append
    with open(cfg_path) as f:
        cfg = f.readlines()
    for line in cfg:
        line = line.strip()
        # Okay, okay, maybe the walrus operator is a good idea.

        # SPECIFICATION
        match = re.match("SPECIFICATION (\w+)", line)
        if match:
            out["spec"] = match[1]

        # INVARIANT
        match = re.match("INVARIANT (\w+)", line)
        if match:
            out["invariants"].append(match[1])

        # TEMPORAL PROPERTIES
        match = re.match("PROPERTY (\w+)", line)
        if match:
            out["properties"].append(match[1])

        # CONSTANTS
        # This regex is imperfect for ordinary assignments
        match = re.match("(\S+)\s?=\s?(.+)", line)
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
    cfg_dict["invariants"] = list(set(cfg_dict["invariants"]))

    cfg_dict["properties"] += args.property
    cfg_dict["properties"] = list(set(cfg_dict["properties"]))

    cfg_dict["constants"] += args.constant
    cfg_dict["constants"] = list(set(cfg_dict["constants"]))

    cfg_dict["model_values"] += args.model_values
    # TODO filter out no-invariants

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
        out.append("CONSTANTS \* regular assignments")
        for constant, value in cfg_dict["constants"]:
            out.append(f"  {constant} = {value}")
    return "\n".join(out)

parser = argparse.ArgumentParser()
cfg_args = parser.add_argument_group("cfg_args", "Configuration values for the TLA+ spec")
tlc_args = parser.add_argument_group("tlc_args", "Runtime values for the TLC model checker")
cfg_args.add_argument("--spec", "--specification", default="Spec", help="The TLA+ specification operator, defaults to Spec")
cfg_args.add_argument("--cfg", help="A template cfg for default values")
cfg_args.add_argument("--invariant", default=[], action="append", nargs='*', help="Adds argument as model invariant, may be specified multiple times")
cfg_args.add_argument("--no-invariant", default=[], action="append", help="Invariants that should NOT be checked")
cfg_args.add_argument("--property", default=[], action="append", nargs='*', help="Adds argument as model temporal property, may be specified multiple times")
cfg_args.add_argument("--no-property", default=[], action="append", help="Temporal Property that should NOT be checked")

cfg_args.add_argument("--constant", default=[], nargs=2, action="append", help="Constants???")
cfg_args.add_argument("--model-values", default=[], nargs='+', help="Constants???")

parser.add_argument("Specfile", help="The specfile.tla")
args = parser.parse_args()

# Flatten invariants plz
args.invariant = list(chain.from_iterable(args.invariant))
args.property = list(chain.from_iterable(args.property))

# We need constants to be a list of tuples for flattening purposes
args.constant = [(x, y) for x, y in args.constant]


cfg = construct_cfg(args=args)
# We don't use the temporary module because it closes the file when we're done, and we need to pass a filepath into tlc.
cfg_file = "temporary.cfg"

print(cfg)
with open(cfg_file, 'w') as f:
    f.write(cfg)
#tla2tools.jar
# TODO os.path
script = f"java -jar {sys.path[0]}\\tla2tools.jar -workers 6 -config {cfg_file} -terse -cleanup {args.Specfile}"
result = subprocess.call(script, shell=True)

sys.exit(result)
# DOes this seriously create an empty folder even when we cleanup the states?!
