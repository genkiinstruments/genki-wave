from dataclasses import dataclass

import pytest

from pywave.genki_wave.data_organization import flatten_nested_dataclass_fields, flatten_nested_dicts


@pytest.mark.parametrize(
    "input_d, expected",
    (
        ({"a": 1, "b": 2}, {"a": 1, "b": 2}),
        ({"a": {}}, {}),
        ({"a": {"b": {"c": 1}, "d": 2}, "e": 3}, {"a_b_c": 1, "a_d": 2, "e": 3}),
        ({}, {}),
    ),
)
def test_flatten_nested_dicts(input_d, expected):
    actual = flatten_nested_dicts(input_d, None)
    assert actual == expected


@dataclass
class A:
    x: float
    y: float


@dataclass
class B:
    a: A
    b: int


@dataclass
class C:
    a: A
    b: B
    c: float


@pytest.mark.parametrize(
    "input_dataclass, expected",
    ((A, ["x", "y"]), (B, ["a_x", "a_y", "b"]), (C, ["a_x", "a_y", "b_a_x", "b_a_y", "b_b", "c"])),
)
def test_flatten_nested_dataclass_fields(input_dataclass, expected):
    actual = flatten_nested_dataclass_fields(input_dataclass, None)
    assert actual == expected
