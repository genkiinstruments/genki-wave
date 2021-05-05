import struct
from dataclasses import Field, asdict, dataclass
from enum import IntEnum
from struct import unpack_from
from typing import Optional, Union


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


class DeviceMode(IntEnum):
    PRESET = 100
    SOFTWAVE = 101
    WAVEFRONT = 102
    API = 103


class PackageType(IntEnum):
    REQUEST = 1
    RESPONSE = 2
    STREAM = 3


class PackageId(IntEnum):
    DATASTREAM = 1
    BATTERY_STATUS = 2
    DEVICE_INFO = 3
    BUTTON_EVENT = 4
    DEVICE_MODE = 5
    IDENTIFY = 6
    RECENTER = 7
    DISPLAY_FRAME = 8


@dataclass(frozen=True)
class PackageMetadata:
    """
    This is called `Query` in the public types header file. Splits out and holds the metadata from each package received
    """

    _fmt = "<BBH"

    type: PackageType
    id: PackageId
    payload_size: int

    @classmethod
    def from_raw_bytes(cls, raw_bytes: Union[bytearray, bytes]) -> "PackageMetadata":
        # TODO(robert): Check annotation `bytes`
        q_type, q_id, q_payload_size = unpack_from(cls._fmt, raw_bytes, 0)
        return cls(type=q_type, id=q_id, payload_size=q_payload_size)

    @classmethod
    def split_out_data_from_metadata(cls, raw_bytes: Union[bytearray, bytes]) -> Union[bytearray, bytes]:
        return raw_bytes[struct.calcsize(cls._fmt) :]

    def to_bytes(self) -> bytes:
        return struct.pack(self._fmt, self.type, self.id, self.payload_size)

    def is_data(self):
        return self.id == PackageId.DATASTREAM

    def is_button(self):
        return self.id == PackageId.BUTTON_EVENT


@dataclass(frozen=True)
class DataPackage:
    """Represents a data package sent from wave

    Note: Initializing DataClasses is (relatively) slow, if in the unlikely event this becomes a bottleneck,
          refactor into a new structure
    """

    _raw_len = 105

    gyro: Point3d
    accel: Point3d
    mag: Point3d
    raw_pose: Point4d
    current_pose: Point4d
    euler: Euler3d
    linear: Point3d
    peak: bool
    peak_norm_velocity: float
    timestamp_us: int

    @classmethod
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "DataPackage":
        # Explanation for the byte structure: https://docs.python.org/3/library/struct.html
        assert len(data) == cls._raw_len, f"Expected the raw data to have len={cls._raw_len}, got len={len(data)}"
        # These parameters encode how to read the bytes from the stream
        return cls(
            gyro=Point3d(*unpack_from("<3f", data, 0)),
            accel=Point3d(*unpack_from("<3f", data, 12)),
            mag=Point3d(*unpack_from("<3f", data, 24)),
            raw_pose=Point4d(*unpack_from("<4f", data, 36)),
            current_pose=Point4d(*unpack_from("<4f", data, 52)),
            euler=Euler3d(*unpack_from("<3f", data, 68)),
            linear=Point3d(*unpack_from("<3f", data, 80)),
            peak=unpack_from("?", data, 92)[0],
            peak_norm_velocity=unpack_from("<f", data, 93)[0],
            timestamp_us=unpack_from("<Q", data, 97)[0],
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
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "ButtonEvent":
        """Decomposes raw bytes into its components and returns them as a :class:`ButtonEvent`"""
        assert len(data) == cls._raw_len, f"Expected to get {cls._raw_len} bytes, got {len(data)}"
        button_id, action = unpack_from("<BB", data, 0)
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
    q = PackageMetadata.from_raw_bytes(raw_bytes)
    raw_bytes_data = PackageMetadata.split_out_data_from_metadata(raw_bytes)

    if q.is_data():
        package = DataPackage.from_raw_bytes(raw_bytes_data)
    elif q.is_button():
        package = ButtonEvent.from_raw_bytes(raw_bytes_data)
    else:
        raise ValueError(f"Unknown value for q.id={q.id}")

    return package
