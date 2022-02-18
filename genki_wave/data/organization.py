import struct
from dataclasses import Field, asdict, dataclass, field
from struct import unpack_from
from typing import Optional, Union

from genki_wave.data.enums import ButtonAction, ButtonId, PackageId, PackageType
from genki_wave.data.points import Euler3d, Point3d, Quaternion, rotate_vector


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
    acc: Point3d
    mag: Point3d
    raw_pose: Quaternion
    current_pose: Quaternion
    euler: Euler3d
    linacc: Point3d
    peak: bool
    peak_norm_velocity: float
    timestamp_us: int
    grav: Point3d = field(init=False)
    acc_glob: Point3d = field(init=False)
    linacc_glob: Point3d = field(init=False)

    def __post_init__(self):
        # A way to initialize a derived field in a frozen dataclass
        super().__setattr__("grav", self.acc - self.linacc)
        super().__setattr__("acc_glob", rotate_vector(self.acc, self.current_pose))
        super().__setattr__("linacc_glob", rotate_vector(self.linacc, self.current_pose))

    @classmethod
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "DataPackage":
        # Explanation for the byte structure: https://docs.python.org/3/library/struct.html
        assert len(data) == cls._raw_len, f"Expected the raw data to have len={cls._raw_len}, got len={len(data)}"
        # These parameters encode how to read the bytes from the stream
        return cls(
            gyro=Point3d(*unpack_from("<3f", data, 0)),
            acc=Point3d(*unpack_from("<3f", data, 12)),
            mag=Point3d(*unpack_from("<3f", data, 24)),
            raw_pose=Quaternion(*unpack_from("<4f", data, 36)),
            current_pose=Quaternion(*unpack_from("<4f", data, 52)),
            euler=Euler3d(*unpack_from("<3f", data, 68)),
            linacc=Point3d(*unpack_from("<3f", data, 80)),
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
