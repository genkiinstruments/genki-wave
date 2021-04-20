import glob
import sys

import serial


LINUX = "linux"
DARWIN = "darwin"


def get_system() -> str:
    if sys.platform.startswith(LINUX):
        return LINUX
    elif sys.platform.startswith(DARWIN):
        return DARWIN
    else:
        raise OSError(f"Unsupported system for serial reading: {sys.platform}")


SYSTEM_TO_SERIAL_PORT_GLOB = {LINUX: "/dev/ttyUSB*", DARWIN: "/dev/tty.usbserial*"}


def get_serial_port() -> str:
    """Get the serial port based on the system"""
    serial_port_glob = SYSTEM_TO_SERIAL_PORT_GLOB[get_system()]
    serial_ports = sorted(glob.glob(serial_port_glob))

    if not serial_ports:
        raise serial.SerialException("No serial port found. Is your serial cable plugged in?")

    return serial_ports[0]


DEFAULT_BLE_ADDRESS = {LINUX: "D5:73:DB:85:B4:A1", DARWIN: "b171e34e-9454-4d6d-b3d0-8740b703b66e"}[get_system()]
