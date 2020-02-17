from pytest import fixture

@fixture
def cfg_fixture():
    return r"""SPECIFICATION Spec
INVARIANT StateInvariant
INVARIANT TypeInvariant
PROPERTY Property1
PROPERTY Property2

CONSTANTS \* model values
  NULL = NULL
  t1 = t1
  t2 = t2
CONSTANTS \* regular assignments
  x = 1
  y = 2"""