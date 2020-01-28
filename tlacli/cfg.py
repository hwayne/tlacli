"""TLC needs to read a .cfg file for invariants etc.
CFG is an internal format with a translatable cfg format.

Terms: "cfg" is short for "config", but "config" includes
TLC tuning, output vals, etc, most not part of .cfg.
"cfg" is the representation JUST the .cfg files 

See Specifying Systems, pg ??? for more info on format
"""

import typing as t

#    We store everything as sets if possible to make merging easier.
ss = t.Set[str] # String set

class CFG:
    """
    Internal representation of a .cfg.
    """

    def __init__(self,
        spec="Spec",
        invariants: ss=set(),
        properties: ss=set(),
        constants=None,
        model_values: ss=set()    
    ):
        self.spec = spec
        self.invariants = invariants
        self.properties = properties
        if constants:
            self.constants = constants
        else:
            self.constants = {}
        self.model_values = model_values

    def to_dict(self):
        return {
        "spec": self.spec,
        "invariants": self.invariants,
        "properties": self.properties,
        "constants": self.constants,
        "model_values": self.model_values,
        }
    def __repr__(self):
        return str(self.to_dict())

    def merge(self, other: 'CFG') -> 'CFG':
        """Merge:
        """
        out = CFG()
        out.invariants = self.invariants | other.invariants
        out.properties = self.properties | other.properties
        out.model_values = self.model_values | other.model_values
        
        # if two CFGs def the same constant, we use the _second_ one
        out.constants.update(self.constants)
        out.constants.update(other.constants)
        return out

    def __eq__(self, other: 'CFG') -> bool:
        """Two CFGs are equal if all of their properties are equal."""
        return self.to_dict() == other.to_dict()
    

def format_cfg(cfg: CFG) -> str:
    cfg_dict = cfg.to_dict()
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