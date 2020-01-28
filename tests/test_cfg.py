
from ..tlacli.tlacli import construct_cfg, extract_cfg, format_cfg
from ..tlacli.cfg import CFG
from hypothesis import given, assume
import hypothesis.strategies as s

def list_sample(sample):
    return s.lists(s.sampled_from(sample), unique=True)

def set_sample(sample):
    return s.sets(s.sampled_from(sample))

def CfgStrategy():
    return s.builds(
        CFG,
        spec=s.just("Spec"),
        invariants=set_sample(("I1", "I2")),
        properties=set_sample(("P1", "P2")),
        constants=s.dictionaries(s.sampled_from(("a", "b", "c")), s.booleans()), # dict()
#        model_values=s.just(set()),
    )




def OldCfgStrategy(*, 
    invariants=s.none(),
    spec=s.just("Spec"),
    props=s.none()):
    
    return s.fixed_dictionaries(
        {
            "spec": spec,
            "invariants": list_sample(("I1", "I2")),
            "properties": list_sample(("P1", "P2")),
            "constants": s.dictionaries(s.sampled_from(("a", "b", "c")), s.booleans()), # dict()
            "model_values": s.just([]),
        }
    )

def test_extract_cfg():
    cfg = extract_cfg("tests/fixtures/1.cfg")
    assert cfg['invariants'] == ['TypeInvariant', 'StateInvariant']
    assert cfg['constants'] == {'x': '1', 'y': '2'}

def test_round_trip():
    with open("tests/fixtures/1.cfg") as f:
        compare = f.read()
    cfg = extract_cfg("tests/fixtures/1.cfg")
    assert format_cfg(cfg) == compare
#    out = construct_cfg(flags_cfg=cfg)


# Default of SPECIFICATION Spec
# Roundtrip cfg <- With this we can stop looking at the raw values of fixtures, we just need to extract them
# # Could be a property test

@given(CfgStrategy(), CfgStrategy())
def test_merge_additive_invariants(f, g):
    out = f.merge(g)
    assert out.invariants == f.invariants | g.invariants
    assert out.properties == f.properties | g.properties

@given(CfgStrategy(), CfgStrategy())
def test_merge_uses_right_constants(f, g):
    out = g.merge(f)
    # g may add entirely new keys
    for c, val in out.constants.items():
        assert (
            (c not in f.constants.keys() 
               and g.constants[c] == val)
            or
            (f.constants[c] == val)

        )

@given(CfgStrategy())
def test_strat(f):
    f

@given(OldCfgStrategy())
def test_fuzz(f):
    format_cfg(construct_cfg(f))

@given(CfgStrategy())
def test_identity(f):
    assert f.merge(CFG()) == CFG().merge(f) == f


@given(OldCfgStrategy(), OldCfgStrategy())
def test_additive_invariants(f, g):
    out = construct_cfg(f, template_cfg=g)
    assert set(out["invariants"]) == set(f["invariants"]) | set(g["invariants"])
    assert set(out["properties"]) == set(f["properties"]) | set(g["properties"])

@given(OldCfgStrategy(), OldCfgStrategy())
def test_prefer_flag_assignments(f, g):
    out = construct_cfg(f, template_cfg=g)
    # g may add entirely new keys
    for c, val in out["constants"].items():
        assert (
            (c not in f["constants"].keys() 
               and g["constants"][c] == val)
            or
            (f["constants"][c] == val)

        )
 
# flags are added to existing cfg
# flag constants overwrite constants in cfg
