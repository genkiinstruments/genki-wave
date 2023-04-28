from __future__ import annotations

import struct
from dataclasses import Field, dataclass, field
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

    def is_device_info(self):
        return self.id == PackageId.DEVICE_INFO

    def is_raw_gyro_accel(self):
        return self.id == PackageId.RAW_DATA

    def is_spectrogram(self):
        return self.id == PackageId.SPECTROGRAM


@dataclass(frozen=True)
class DataPackage:
    """Represents a data package sent from wave

    Note: Initializing DataClasses is (relatively) slow, if in the unlikely event this becomes a bottleneck,
          refactor into a new structure
    """

    _raw_len = 105
    _raw_gyro_accel_len = 32

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

    def as_dict(self) -> dict:
        # This is (and should be) equivalent to `asdict(self)`, but is about 20-30x faster since it doesn't have
        # to recursively expand all dataclass fields
        return {
            "gyro": self.gyro.as_dict(),
            "acc": self.acc.as_dict(),
            "mag": self.mag.as_dict(),
            "raw_pose": self.raw_pose.as_dict(),
            "current_pose": self.current_pose.as_dict(),
            "euler": self.euler.as_dict(),
            "linacc": self.linacc.as_dict(),
            "peak": self.peak,
            "peak_norm_velocity": self.peak_norm_velocity,
            "timestamp_us": self.timestamp_us,
            "grav": self.grav.as_dict(),
            "acc_glob": self.acc_glob.as_dict(),
            "linacc_glob": self.linacc_glob.as_dict(),
        }

    def as_flat_dict(self) -> dict:
        # This is (and should be) equivalent to `flatten_nested_dicts(asdict(self))`, but is about 20-30x faster since
        # it doesn't have to recursively expand all dataclass fields
        return {
            **self.gyro.as_dict("gyro_"),
            **self.acc.as_dict("acc_"),
            **self.mag.as_dict("mag_"),
            **self.raw_pose.as_dict("raw_pose_"),
            **self.current_pose.as_dict("current_pose_"),
            **self.euler.as_dict("euler_"),
            **self.linacc.as_dict("linacc_"),
            "peak": self.peak,
            "peak_norm_velocity": self.peak_norm_velocity,
            "timestamp_us": self.timestamp_us,
            **self.grav.as_dict("grav_"),
            **self.acc_glob.as_dict("acc_glob_"),
            **self.linacc_glob.as_dict("linacc_glob_"),
        }

    @classmethod
    def flat_keys(cls) -> tuple:
        return tuple(flatten_nested_dataclass_fields(cls, None))


@dataclass(frozen=True)
class RawDataPackage:
    """Represents a package of raw data (just acc, gyro, and timestamp) sent from wave"""

    _raw_len = 32

    gyro: Point3d
    acc: Point3d
    timestamp_us: int

    @classmethod
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "RawDataPackage":
        # Explanation for the byte structure: https://docs.python.org/3/library/struct.html
        if len(data) != cls._raw_len:
            raise ValueError(f"Expected the raw gyro/accel data to have len={cls._raw_len}, got len={len(data)}", data)

        # These parameters encode how to read the bytes from the stream
        return cls(
            gyro=Point3d(*unpack_from("<3f", data, 0)),
            acc=Point3d(*unpack_from("<3f", data, 12)),
            timestamp_us=unpack_from("<Q", data, 24)[0],
        )

    def as_dict(self) -> dict:
        # This is (and should be) equivalent to `asdict(self)`, but is about 20-30x faster since it doesn't have
        # to recursively expand all dataclass fields
        return {"gyro": self.gyro.as_dict(), "acc": self.acc.as_dict(), "timestamp_us": self.timestamp_us}

    def as_flat_dict(self) -> dict:
        # This is (and should be) equivalent to `flatten_nested_dicts(asdict(self))`, but is about 20-30x faster since
        # it doesn't have to recursively expand all dataclass fields
        return {**self.gyro.as_dict("gyro_"), **self.acc.as_dict("acc_"), "timestamp_us": self.timestamp_us}

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


@dataclass(frozen=True)
class DeviceInfo:
    """Represents a button event sent from wave"""

    _raw_len = 35

    version: str
    board_version: str
    mac_address: str
    serial_number: str

    @classmethod
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "DeviceInfo":
        """Decomposes raw bytes into its components and returns them as a :class:`ButtonEvent`"""
        assert len(data) == cls._raw_len, f"Expected to get {cls._raw_len} bytes, got {len(data)}"

        version = unpack_from("<3B", data[0:3])
        board_version = unpack_from("9s", data[3:12])
        mac_address = unpack_from("<6B", data[12:18])
        serial_number = unpack_from("17s", data[18:35])

        return cls(
            version=".".join(f"{x}" for x in version),
            board_version=board_version[0].decode("utf-8").rstrip("\x00"),
            mac_address=":".join(f"{b:02x}" for b in mac_address).strip().upper(),
            serial_number=serial_number[0].decode("utf-8").rstrip("\x00"),
        )


@dataclass(frozen=True)
class SpectrogramDataPackage:
    """Represents a column in a spectrogram sent from wave"""

    _num_bins_per_channel = 16
    _num_channels = 6
    _num_floats = _num_bins_per_channel * _num_channels

    _data_len = _num_floats * 4
    _timestamp_bytes = 8
    _raw_len = _data_len + _timestamp_bytes

    _data_format_str = f"<{_num_floats}f"

    data: list[float]
    timestamp_us: int

    @classmethod
    def from_raw_bytes(cls, data: Union[bytearray, bytes]) -> "SpectrogramDataPackage":
        if len(data) != cls._raw_len:
            raise ValueError(f"Expected spectrogram data to have len={cls._raw_len}, got len={len(data)}", data)

        return cls(
            data=[x for x in unpack_from(cls._data_format_str, data, 0)],
            timestamp_us=unpack_from("<Q", data, cls._data_len)[0],
        )

    def _channel_slice(self, index) -> list:
        start = index * self._num_bins_per_channel
        s = slice(start, start + self._num_bins_per_channel, None)
        return self.data[s]

    def as_dict(self) -> dict:
        # This is (and should be) equivalent to `asdict(self)`, but is about 20-30x faster since it doesn't have
        # to recursively expand all dataclass fields
        return {
            "acc_x": self._channel_slice(0),
            "acc_y": self._channel_slice(1),
            "acc_z": self._channel_slice(2),
            "gyro_x": self._channel_slice(3),
            "gyro_y": self._channel_slice(4),
            "gyro_z": self._channel_slice(5),
            "timestamp_us": self.timestamp_us,
        }


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


def process_byte_data(raw_bytes: Union[bytearray, bytes]) -> Union[ButtonEvent, DataPackage, RawDataPackage]:
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
    elif q.is_device_info():
        package = DeviceInfo.from_raw_bytes(raw_bytes_data)
    elif q.is_raw_gyro_accel():
        package = RawDataPackage.from_raw_bytes(raw_bytes_data)
    elif q.is_spectrogram():
        package = SpectrogramDataPackage.from_raw_bytes(raw_bytes_data)
    else:
        raise ValueError(f"Unknown value for q.id={q.id}")

    return package


Package = Union[DataPackage, RawDataPackage, SpectrogramDataPackage]
