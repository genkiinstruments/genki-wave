from dataclasses import dataclass

import pytest

from genki_wave.data.organization import PackageMetadata, flatten_nested_dataclass_fields, flatten_nested_dicts


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


@pytest.mark.parametrize(
    "q_type, q_id, q_payload_size, expected", [[3, 1, 93, b"\x03\x01]\x00"], [1, 5, 1, b"\x01\x05\x01\x00"]]
)
def test_package_metadata_to_bytes(q_type, q_id, q_payload_size, expected):
    p = PackageMetadata(type=q_type, id=q_id, payload_size=q_payload_size)
    actual = p.to_bytes()
    assert actual == expected


@pytest.mark.parametrize("input_and_expected", [b"\x03\x01]\x00", b"\x01\x05\x01\x00"])
def test_package_metadata_to_bytes_sanity_check(input_and_expected):
    p = PackageMetadata.from_raw_bytes(input_and_expected)
    actual = p.to_bytes()
    assert actual == input_and_expected
