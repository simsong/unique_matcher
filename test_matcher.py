#!/usr/bin/env python36

from collections import defaultdict
import csv
import pytest
from matcher import *


def test_strkeys():
    keys = frozenset([1])
    assert strkeys(keys)=="1"

    keys = frozenset([1,2])
    assert strkeys(keys)=="1 2"

def test_choose_all_subkeys():
    keys = frozenset([1,2,3])
    sk   = choose_all_subkeys(keys)
    sk.remove(frozenset([1,2]))
    sk.remove(frozenset([2,3]))
    sk.remove(frozenset([1,3]))
    assert sk==[]


