from dataclasses import dataclass
from wave.data_organization import (
    ButtonAction,
    ButtonEvent,
    ButtonId,
    DataPackage,
    Euler3d,
    Point3d,
    Point4d,
    flatten_nested_dataclass_fields,
    flatten_nested_dicts,
    process_byte_data,
)
import pytest


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
    "input_raw, expected",
    (
        (
            b"\x02\x04\x08\x00\x01\x01\x00\x00\xf0P\x96C",
            ButtonEvent(button_id=ButtonId.MIDDLE, action=ButtonAction.DOWN),
        ),
        (
            bytearray(b"\x02\x04\x08\x00\x00\x01\x00\x00\x902VC"),
            ButtonEvent(button_id=ButtonId.TOP, action=ButtonAction.DOWN),
        ),
        (
            (
                b"\x03\x01]\x00X\xf4\r>\x88n\xfc\xbdQs\xaf>\x000w\xbf\x00\x00%\xbd\x00\xe0\x90\xbe\x97L\x16\xbf\xef"
                b"\x15\t\xbeg;I\xbf\x86\x00\x02>\x97L\x16\xbf\xef\x15\t\xbeg;I\xbf\x86\x00\x02>;'?\xc0/c\xa3\xbf\xa6"
                b"\xa6:\xc0\x80\x93\x0c\xbc\x10[\n;@ \x96\xbb\x00\x00\x00\x00\x00\x93\x8f\xe5*\x00\x00\x00\x00"
            ),
            DataPackage(
                gyro=Point3d(x=0.13862740993499756, y=-0.12325769662857056, z=0.34267666935920715),
                accel=Point3d(x=-0.965576171875, y=-0.040283203125, z=-0.282958984375),
                raw_pose=Point4d(
                    w=-0.5871061682701111, x=-0.13387273252010345, y=-0.7860626578330994, z=0.12695512175559998
                ),
                current_pose=Point4d(
                    w=-0.5871061682701111, x=-0.13387273252010345, y=-0.7860626578330994, z=0.12695512175559998
                ),
                euler=Euler3d(roll=-2.986769437789917, pitch=-1.2764643430709839, yaw=-2.916421413421631),
                linear=Point3d(x=-0.00858008861541748, y=0.002111140638589859, z=-0.004581481218338013),
                peak=False,
                peak_norm_velocity=0.0,
                timestamp_us=719687571,
            ),
        ),
        (
            bytearray(
                b"\x03\x01]\x00\x82\x98\xff\xc2PB\xde\xc2R\xed\xd4\xc1\x00P`\xbf\x00\x80\x84>\x00\xc0\x1f\xbf\xf8\xd1"
                b"\x95\xbe\x94\x1f\x1e>\x92ig\xbfS|\x87\xbe\xf8\xd1\x95\xbe\x94\x1f\x1e>\x92ig\xbfS|\x87\xbe\x18\xf4'@"
                b"\xa31(\xbf\xd9\xdf>@\xca\xeb\x87\xbe&Z\x04\xbe8v\x84=\x00\x00\x00\x00\x00\x0bF\x0fd\x00\x00\x00\x00"
            ),
            DataPackage(
                gyro=Point3d(x=-127.79786682128906, y=-111.1295166015625, z=-26.61587905883789),
                accel=Point3d(x=-0.876220703125, y=0.2587890625, z=-0.6240234375),
                raw_pose=Point4d(
                    w=-0.2926175594329834, x=0.15441733598709106, y=-0.9039546251296997, z=-0.2646203935146332
                ),
                current_pose=Point4d(
                    w=-0.2926175594329834, x=0.15441733598709106, y=-0.9039546251296997, z=-0.2646203935146332
                ),
                euler=Euler3d(roll=2.6242733001708984, pitch=-0.6570073962211609, yaw=2.982412576675415),
                linear=Point3d(x=-0.26547080278396606, y=-0.12925013899803162, z=0.0646786093711853),
                peak=False,
                peak_norm_velocity=0.0,
                timestamp_us=1678722571,
            ),
        ),
    ),
    ids=["button_serial", "button_bluetooth", "data_serial", "data_bluetooth"],
)
def test_process_byte_data(input_raw, expected):
    actual = process_byte_data(input_raw)
    assert actual == expected
