"""TLC needs to read a .cfg file for invariants etc.
CFG is an internal format with a translatable cfg format.

Terms: "cfg" is short for "config", but "config" includes
TLC tuning, output vals, etc, most not part of .cfg.
"cfg" is the representation JUST the .cfg files 

See Specifying Systems, pg ??? for more info on format
"""

import typing as t
from dataclasses import dataclass, field, asdict
#    We store everything as sets if possible to make merging easier.
ss = t.Set[str] # String set

@dataclass
class CFG:
    """
    Internal representation of a .cfg.
    """
    spec: t.Optional[str] = None
    invariants: ss = field(default_factory=set)
    properties: ss = field(default_factory=set)
    constants: t.Dict[str, str] = field(default_factory=dict)
    model_values: ss = field(default_factory=set)

    def merge(self, other: 'CFG') -> 'CFG':
        """Merge two CFGs to get a new combined CFG.
        New CFG is created, inputs are not modified

        sets are unioned, dicts with shared keys use the value of `other`
        """
        out = CFG()
        out.invariants = self.invariants | other.invariants
        out.properties = self.properties | other.properties
        out.model_values = self.model_values | other.model_values

        out.spec = other.spec or self.spec

        # if two CFGs def the same constant, we use the _second_ one
        out.constants.update(self.constants)
        out.constants.update(other.constants)
        return out

def format_cfg(cfg: CFG) -> str:
    """Convert a CFG into a format that can be read by TLC."""
    # XXX temporarily just using sorted to enforce ordering
    spec = cfg.spec or "Spec"
    out = [f"SPECIFICATION {spec}"]
    for inv in sorted(cfg.invariants):
        out.append(f"INVARIANT {inv}")

    for prop in sorted(cfg.properties):
        out.append(f"PROPERTY {prop}")

    if cfg.model_values:
        out.append("\nCONSTANTS \\* model values")
        for model in sorted(cfg.model_values):
            out.append(f"  {model} = {model}")


    # TODO should this use <- instead of = ?
    # Would break the regex for reading in cfgs
    if cfg.constants:
        out.append(r"CONSTANTS \* regular assignments")
        for constant, value in cfg.constants.items():
            out.append(f"  {constant} = {value}")
    return "\n".join(out)


