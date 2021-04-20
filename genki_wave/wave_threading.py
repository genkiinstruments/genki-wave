import asyncio
import threading
from typing import Callable, Optional

import serial
from serial import Serial
from serial.threaded import ReaderThread

from genki_wave.constants import BAUDRATE
from genki_wave.protocols import ProtocolThreadSerial, ProtocolThreadBluetooth
from genki_wave.utils import get_serial_port, get_or_create_and_set_event_loop
from genki_wave.wave_asyncio import producer_bluetooth, CommunicateCancel


class ReaderThreadSerial(ReaderThread):
    """A thin wrapper around `serial.threaded.ReaderThread`"""

    def __init__(self, serial_instance: Serial, protocol_factory: Callable):
        super().__init__(serial_instance, protocol_factory)

    @classmethod
    def from_port(cls, serial_port: Optional[str] = None) -> "ReaderThreadSerial":
        port = get_serial_port() if serial_port is None else serial_port
        serial_instance = Serial(port, BAUDRATE, parity=serial.PARITY_EVEN)
        return cls(serial_instance, ProtocolThreadSerial)


class ReaderThreadBluetooth(threading.Thread):
    """An (not fully worked out) imitation of `serial.threaded.ReaderThread` for the bluetooth interface

    Note: Methods that clean up the connection are not fully worked out

    Note: Since the library used to interface with bluetooth only has an interface using `asyncio`, this
          uses the async code in a separate thread and then gets the data from there.
    """

    def __init__(self, ble_address, protocol_factory):
        super().__init__(daemon=True)
        self.protocol_factory = protocol_factory
        self.protocol = None
        self.alive = True
        self._lock = threading.Lock()
        self._comm = CommunicateCancel()
        self._ble_address = ble_address

    @classmethod
    def from_address(cls, ble_address: str) -> "ReaderThreadBluetooth":
        return cls(ble_address, ProtocolThreadBluetooth)

    def stop(self):
        """Stop the reader thread"""
        self.alive = False
        self.join(2)

    @staticmethod
    def run_producer(protocol, comm, ble_address) -> None:
        """Runs a producer

        Args:
            comm:
            protocol:
            ble_address: Address of the bluetooth device to connect to. E.g. 'D5:73:DB:85:B4:A1'. If `None` it
                         connects via serial
        """
        producer = producer_bluetooth(protocol, comm, ble_address)
        get_or_create_and_set_event_loop()
        # TODO(robert): Catch a keyboard interrupt and gracefully shut down. Non-trivial to implement.
        tasks = asyncio.gather(*[producer])
        asyncio.get_event_loop().run_until_complete(tasks)

    def run(self):
        """Reader loop"""
        self.protocol = self.protocol_factory()
        self.run_producer(self.protocol, self._comm, self._ble_address)

    def close(self):
        with self._lock:
            self._comm.cancel = True
            self.stop()

    def __enter__(self):
        """Enter context: Start code"""
        self.start()
        return self.protocol

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Leave context: close port"""
        self.close()
