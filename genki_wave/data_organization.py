from dataclasses import dataclass, asdict, Field
from enum import IntEnum
from typing import Optional, Union

from genki_wave.data_stream_manipulation import unpack_bytes, split_byte_data


class ButtonId(IntEnum):
    """Which button is a package representing"""

    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


class ButtonAction(IntEnum):
    """The action of a button package

    Up: button was released
    Down: button was pressed down
    Long: a long press was detected (button down for 500ms or more)
    LongUp: a long press was released (I think you'll always receive an "up" event with this one)
    ExtraLong: an extra long press was detected (I think it's about 2000ms, you'll always receive a "long" event
               before this one)
    ExtraLongUp: button released after an "extra long" press
    Click: button was pressed down and released "quickly" (i.e. not triggering a long press)
    DoubleClick: not used
    """

    UP = 0
    DOWN = 1
    LONG = 2
    LONGUP = 3
    EXTRALONG = 4
    EXTRALONGUP = 5
    CLICK = 6
    DOUBLECLICK = 7


class PackageType(IntEnum):
    DATA = 1
    BUTTON = 4


@dataclass(frozen=True)
class Point3d:
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Point4d:
    w: float
    x: float
    y: float
    z: float


@dataclass(frozen=True)
class Euler3d:
    roll: float
    pitch: float
    yaw: float


@dataclass(frozen=True)
class DataPackage:
    """Represents a data package sent from wave

    Note: Initializing DataClasses is (relatively) slow, if in the unlikely event this becomes a bottleneck,
          refactor into a new structure
    """

    _raw_len = 93

    gyro: Point3d
    accel: Point3d
    raw_pose: Point4d
    current_pose: Point4d
    euler: Euler3d
    linear: Point3d
    peak: bool
    peak_norm_velocity: float
    timestamp_us: int

    @classmethod
    def from_raw_bytes(cls, data: bytearray) -> "DataPackage":
        # Explanation for the byte structure: https://docs.python.org/3/library/struct.html
        assert len(data) == cls._raw_len, f"Expected the raw data to have len={cls._raw_len}, got len={len(data)}"
        # These parameters encode how to read the bytes from the stream
        return cls(
            gyro=Point3d(*unpack_bytes("<3f", data[0:12])),
            accel=Point3d(*unpack_bytes("<3f", data[12:24])),
            raw_pose=Point4d(*unpack_bytes("<4f", data[24:40])),
            current_pose=Point4d(*unpack_bytes("<4f", data[40:56])),
            euler=Euler3d(*unpack_bytes("<3f", data[56:68])),
            linear=Point3d(*unpack_bytes("<3f", data[68:80])),
            peak=unpack_bytes("?", data[80:81]),
            peak_norm_velocity=unpack_bytes("<f", data[81:85]),
            timestamp_us=unpack_bytes("<Q", data[85:93]),
        )

    def as_flat_dict(self) -> dict:
        # Recursively unpack into dicts
        d = asdict(self)
        d = flatten_nested_dicts(d, None)
        return d

    @classmethod
    def flat_keys(cls) -> tuple:
        return tuple(flatten_nested_dataclass_fields(cls, None))


@dataclass(frozen=True)
class ButtonEvent:
    """Represents a button event sent from wave"""

    _raw_len = 8
    _relevant_idx = 2

    button_id: ButtonId
    action: ButtonAction

    @classmethod
    def from_raw_bytes(cls, data: bytearray) -> "ButtonEvent":
        """Decomposes raw bytes into its components and returns them as a :class:`ButtonEvent`"""
        assert len(data) == cls._raw_len, f"Expected to get {cls._raw_len} bytes, got {len(data)}"
        button_id, action = unpack_bytes("<BB", data[: cls._relevant_idx])
        return cls(button_id=ButtonId(button_id), action=ButtonAction(action))


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


def flatten_nested_dataclass_fields(d: Union[Field, type], name: Optional[str]) -> list:
    """Analogous to `flatten_nested_dicts`, but returns the key names and works on the static class, not an instance

    Args:
        d: A dataclass e.g. `DataPackage`
        name: The prefix to this level, or more specifically, the key for the next higher level. If `None`, no prefix
              is used

    Returns:
        Returns the concatenated keys

    Examples:
        >>> @dataclass
        ... class A:
        ...     x: float
        ...     y: float
        >>> flatten_nested_dataclass_fields(A, None)
        ['x', 'y']
        >>> @dataclass
        ... class B:
        ...     a: A
        ...     b: int
        >>> flatten_nested_dataclass_fields(B, None)
        ['a_x', 'a_y', 'b']
    """
    results = []
    if hasattr(d, "__dataclass_fields__"):
        for k, v in d.__dataclass_fields__.items():
            curr_name = f"{name}_{k}" if name is not None else k
            curr_val = flatten_nested_dataclass_fields(v, curr_name)
            results.extend(curr_val)
    elif isinstance(d, Field):
        curr_val = flatten_nested_dataclass_fields(d.type, name)
        results.extend(curr_val)
    else:
        results.append(name)

    return results


def process_byte_data(raw_bytes: Union[bytearray, bytes]) -> Union[ButtonEvent, DataPackage]:
    """Factory function that takes raw bytes and translates into a button event or data

    Args:
        raw_bytes: The input raw bytes

    Returns:
        The resulting button event or data
    """
    q_type, q_id, length, data_values = split_byte_data(raw_bytes)

    if q_id == PackageType.DATA:
        package = DataPackage.from_raw_bytes(data_values)
    elif q_id == PackageType.BUTTON:
        package = ButtonEvent.from_raw_bytes(data_values)
    else:
        raise ValueError(f"Unknown value for q_id={q_id}")

    return package
