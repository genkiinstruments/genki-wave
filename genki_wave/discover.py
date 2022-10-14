import asyncio

import bleak


async def discover_bluetooth(device_str: str):
    print("Searching for bluetooth devices...")
    devices = await bleak.BleakScanner.discover()
    wave_devices = [d for d in devices if (d.name is not None) and (device_str in d.name)]
    print("Found the following devices" if wave_devices else "Found no devices")
    for device in wave_devices:
        print(f"Address: {device.address} - Name: {device.name}")


def run_discover_bluetooth():
    """Finds all `Wave` devices available for bluetooth connection and prints the addresses"""
    asyncio.get_event_loop().run_until_complete(discover_bluetooth("Wave"))
