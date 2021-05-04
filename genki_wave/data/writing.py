import struct

from cobs import cobs

from genki_wave.data.organization import DeviceMode, PackageId, PackageMetadata, PackageType


def pad_with_zero_byte(b: bytes) -> bytes:
    return b + struct.pack("<B", 0)


def create_package_to_write(p: PackageMetadata, data: bytes) -> bytes:
    # TODO(robert): `data` should probably be a class that has a `to_bytes` method
    if p.payload_size != len(data):
        raise ValueError(
            f"Expected payload_size and the size of the data to match. Got {p.payload_size} and {len(data)}"
        )
    b_tot = p.to_bytes() + data
    b_encoded = cobs.encode(b_tot)
    b_buffer = pad_with_zero_byte(b_encoded)
    return b_buffer


def start_api_package():
    return create_package_to_write(
        PackageMetadata(type=PackageType.REQUEST, id=PackageId.DEVICE_MODE, payload_size=1),
        struct.pack("<B", DeviceMode.API.value),
    )
