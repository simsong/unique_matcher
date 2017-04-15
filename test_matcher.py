#!/usr/bin/env python36

from matcher import *


class DebugTrue:
    def __init__(self):
        self.debug = True


# Verify that the function works.
def test_strkeys():
    keys = frozenset([1])
    assert strkeys(keys)=="1"

    keys = frozenset([1,2])
    assert strkeys(keys)=="1 2"


# By induction, if the function below works, then choose_all_subkeys() works.
def test_choose_all_subkeys():
    keys = frozenset([1,2,3])
    sk   = choose_all_subkeys(keys)
    sk.remove(frozenset([1,2]))
    sk.remove(frozenset([2,3]))
    sk.remove(frozenset([1,3]))
    assert sk==[]


def test_readrows():
    rows = read_rows("test_data.csv")
    assert rows[0] == ('11111','1','1','1','1')
    assert len(rows)==16


def test_find_singletons():
    import matcher
    matcher.args = DebugTrue()
    all_rows = [(1, 1, 1),
                (1, 2, 3),
                (1, 3, 1)]
    assert find_singletons(all_rows, all_rows, frozenset([0, 1, 2])) == all_rows
    assert find_singletons(all_rows, all_rows, frozenset([0])) == []
    assert find_singletons(all_rows, all_rows, frozenset([1])) == all_rows
    assert find_singletons(all_rows, all_rows, frozenset([2])) == [(1, 2, 3)]
    assert find_singletons(all_rows, all_rows, frozenset([0, 1])) == all_rows
    assert find_singletons(all_rows, all_rows, frozenset([1, 2])) == all_rows
    assert find_singletons(all_rows, all_rows, frozenset([0, 2])) == [(1, 2, 3)]


def test_matcher_py():
    from subprocess import Popen, PIPE
    out = Popen(['python', 'matcher.py'], stdout=PIPE).communicate()[0].decode("utf-8")
    lines = out.split("\n")
    assert lines[0] == "Keys that we will consider: 1 2 3 4"
    assert lines[1] == "Total of all uniques: 123"
