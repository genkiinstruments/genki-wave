import asyncio
import threading
from typing import Callable, Optional

import serial
from serial import Serial
from serial.threaded import ReaderThread

from genki_wave.constants import BAUDRATE
from genki_wave.data.writing import get_start_api_package
from genki_wave.protocols import ProtocolThread, bluetooth_task, CommunicateCancel


from genki_wave.utils import get_serial_port, get_or_create_event_loop
from genki_wave.asyncio_runner import producer_bluetooth


class ReaderThreadSerial(ReaderThread):
    """A thin wrapper around `serial.threaded.ReaderThread`"""

    def __init__(self, serial_instance: Serial, protocol_factory: Callable):
        super().__init__(serial_instance, protocol_factory)
        self.write(get_start_api_package())

    @classmethod
    def from_port(cls, serial_port: Optional[str] = None) -> "ReaderThreadSerial":
        """Create a `ReaderThreadSerial` object from a serial port

        Args:
            serial_port: The serial port to read from. If `None` will automatically determine the port based on the
                operating system.

        Returns:
            An instance of `ReaderThreadSerial` with the specified port
        """
        port = get_serial_port() if serial_port is None else serial_port
        serial_instance = Serial(port, BAUDRATE, parity=serial.PARITY_EVEN)
        return cls(serial_instance, ProtocolThread)


class ReaderThreadBluetooth(threading.Thread):
    """An imitation of `serial.threaded.ReaderThread` for the bluetooth interface

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
        return cls(ble_address, ProtocolThread)

    def stop(self):
        """Stop the reader thread"""
        self.alive = False
        self.join(2)

    @staticmethod
    def run_producer(protocol, comm, ble_address) -> None:
        """Runs a producer fetching the data

        Args:
            comm: An object that allows `producer` and `consumer` to communicate when to cancel a process
            protocol: An object that knows how to process the raw data sent from the Wave ring into a structured format
                  and passes it along
            ble_address: Address of the bluetooth device to connect to. E.g. 'D5:73:DB:85:B4:A1'. If `None` it
                         connects via serial
        """
        loop = get_or_create_event_loop()
        producer = producer_bluetooth(protocol, comm, ble_address)
        tasks = asyncio.gather(*[producer])
        loop.run_until_complete(tasks)

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


class WaveListener(threading.Thread):
    def __init__(self, ble_address, callbacks):
        self.ble_address = ble_address
        self.callbacks = callbacks
        super().__init__()

    def run(self):
        self.comm = CommunicateCancel()
        task = bluetooth_task(self.ble_address, self.comm, self.callbacks)
        loop = get_or_create_event_loop()
        loop.run_until_complete(task)

    def stop(self):
        self.comm.cancel = True

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.stop()
