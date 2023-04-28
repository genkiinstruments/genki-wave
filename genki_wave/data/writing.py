import struct

from cobs import cobs

from genki_wave.data.organization import PackageMetadata
from genki_wave.data.enums import DeviceMode, PackageId, PackageType, DatastreamType


def pad_with_zero_byte(b: bytes) -> bytes:
    return b + struct.pack("<B", 0)


def create_package_to_write(p: PackageMetadata, data: bytes = bytearray()) -> bytes:
    """Package the data in the correct format before sending it to a Wave ring"""
    # TODO(robert): `data` should probably be a class that has a `to_bytes` method
    if p.payload_size != len(data):
        raise ValueError(
            f"Expected payload_size and the size of the data to match. Got {p.payload_size} and {len(data)}"
        )
    b_tot = p.to_bytes() + data
    b_encoded = cobs.encode(b_tot)
    b_buffer = pad_with_zero_byte(b_encoded)
    return b_buffer


def get_start_api_package():
    """Get the package that puts the Wave ring into 'API mode' when it's sent to the device"""
    return create_package_to_write(
        PackageMetadata(type=PackageType.REQUEST, id=PackageId.DEVICE_MODE, payload_size=1),
        struct.pack("<B", DeviceMode.API.value),
    )


def get_start_spectrogram_package():
    """"""
    return create_package_to_write(
        PackageMetadata(type=PackageType.REQUEST, id=PackageId.MODIFY_API_CONFIG, payload_size=8),
        struct.pack("<BBxxf", DatastreamType.NONE.value, True, 2000.0),
    )


def get_default_api_config_package():
    """"""
    return create_package_to_write(
        PackageMetadata(type=PackageType.REQUEST, id=PackageId.MODIFY_API_CONFIG, payload_size=8),
        struct.pack("<BBxxf", DatastreamType.MOTION_DATA.value, False, 400.0),
    )


def get_device_info_request():
    """Get the package that requests device info when it's sent to the device"""
    return create_package_to_write(PackageMetadata(type=PackageType.REQUEST, id=PackageId.DEVICE_INFO, payload_size=0))
