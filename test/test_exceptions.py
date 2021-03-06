from hashbox import HashBox, FrozenHashBox
from hashbox.exceptions import MissingIndexError
from hashbox.constants import SIZE_THRESH
import pytest

from .conftest import AssertRaises, BadHash


def test_remove_empty():
    f = HashBox([], on=["stuff"])
    with AssertRaises(KeyError):
        f.remove("nope")


def test_empty_frozen():
    with AssertRaises(ValueError):
        FrozenHashBox([], on=["stuff"])


def test_no_index_mutable():
    with AssertRaises(ValueError):
        HashBox(["a"])


def test_bad_query(index_type):
    f = index_type([0], on=["a"])
    with AssertRaises(TypeError):
        f.find(match=[])
    with AssertRaises(TypeError):
        f.find(["a", 1])
    with AssertRaises(MissingIndexError):
        f.find({"b": 1})


@pytest.mark.parametrize("n_items", [1, 5, SIZE_THRESH + 1])
def test_remove_missing_value(n_items):
    """
    When the value hashes to a bucket, but the bucket does not contain the value, is
    an empty result correctly retrieved?
    """
    data = [BadHash(i) for i in range(5)]
    f = HashBox(data, ["n"])
    assert len(f.find({"n": -1})) == 0
    with AssertRaises(KeyError):
        f.remove(BadHash(-1))
