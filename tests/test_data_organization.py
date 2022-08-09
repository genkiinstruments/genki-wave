from dataclasses import asdict, dataclass
from typing import Optional

import pytest

from genki_wave.data import Point3d, Quaternion, Euler3d
from genki_wave.data.organization import PackageMetadata, flatten_nested_dataclass_fields, DataPackage, RawDataPackage


def flatten_nested_dicts(d: dict, name: Optional[str]) -> dict:
    """Recursively flattens dicts of dicts into a dict with keys concatenated

    Args:
        d: The dictionary to flatten
        name: The prefix to this level, or more specifically, the key for the next higher level. If `None`, no prefix
              is used

    Returns:
        A flat dict where the keys have been concatenated

    Examples:
        >>> flatten_nested_dicts({"a": {"b": {"c": 1}, "d": 2}, "e": 3}, None)
        {'a_b_c': 1, 'a_d': 2, 'e': 3}
    """
    d_results = {}
    if isinstance(d, dict):
        for k, v in d.items():
            curr_name = f"{name}_{k}" if name is not None else k
            curr_val = flatten_nested_dicts(v, curr_name)
            d_results.update(curr_val)
    else:
        curr_val = {name: d}
        d_results.update(curr_val)

    return d_results


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


@pytest.mark.parametrize(
    "dp",
    [
        DataPackage(
            gyro=Point3d(x=-4.4767, y=24.9753, z=-12.628),
            acc=Point3d(x=-0.0078, y=0.4243, z=0.8977),
            mag=Point3d(x=0.0, y=0.0, z=-0.0),
            raw_pose=Quaternion(w=-0.8855, x=-0.2154, y=-0.0486, z=-0.4046),
            current_pose=Quaternion(w=-0.8855, x=-0.2154, y=-0.0486, z=-0.4046),
            euler=Euler3d(roll=0.4363, pitch=0.0883, yaw=-0.8349),
            linacc=Point3d(x=-0.0960, y=0.0034, z=0.0019),
            peak=False,
            peak_norm_velocity=0.0,
            timestamp_us=29422570,
        ),
        RawDataPackage(gyro=Point3d(x=-4.4, y=24.9, z=-12.6), acc=Point3d(x=0.0, y=0.4, z=0.8), timestamp_us=10),
    ],
)
def test_datapackage_as_dict(dp):
    assert dp.as_dict() == asdict(dp)
    assert dp.as_flat_dict() == flatten_nested_dicts(asdict(dp), None)
