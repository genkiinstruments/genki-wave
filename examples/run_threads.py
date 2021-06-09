import argparse
import time
from typing import Union

from genki_wave.data.organization import ButtonEvent
from genki_wave.discover import run_discover_bluetooth
from genki_wave.threading_runner import ReaderThreadBluetooth, ReaderThreadSerial


class Sleeper:
    """A simple class to sleep for an amount of time that makes sure each loop runs for `sleep_for_x_seconds` seconds"""

    def __init__(self, sleep_for_x_seconds: float):
        self._last_time = None
        self._sleep_for_x_seconds = sleep_for_x_seconds

    def sleep(self):
        curr_time = time.time()
        sleep_time = max(0.0, self._sleep_for_x_seconds - (self.last_time - curr_time))
        time.sleep(sleep_time)
        self._last_time = time.time()

    @property
    def last_time(self):
        if self._last_time is None:
            self._last_time = time.time()
        return self._last_time


def main(reader_thread: Union[ReaderThreadBluetooth, ReaderThreadSerial], fetch_data_every_x_seconds: float):
    """A simple function to showcase reading from a thread.

    Fetches data every `fetch_data_every_x_seconds` and prints out all button presses in that timespan and the
    last value (usually a data package)
    """

    s = Sleeper(fetch_data_every_x_seconds)
    with reader_thread as wave:
        while True:
            val = wave.queue.pop_all()
            if val:
                for v in val:
                    if isinstance(v, ButtonEvent):
                        print(v)
                print(val[-1])

            s.sleep()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ble-address", type=str)
    parser.add_argument("--use-serial", action="store_true")
    parser.add_argument("--fetch-data-every-x-seconds", type=float, default=1.0)
    args = parser.parse_args()

    if args.use_serial:
        main(ReaderThreadSerial.from_port(), args.fetch_data_every_x_seconds)
    else:
        if args.ble_address is None:
            print("No bluetooth address (--ble-address) supplied, searching for devices...")
            run_discover_bluetooth()
        else:
            print("Turn off using Ctrl + C (`KeyboardInterrupt`)")
            main(ReaderThreadBluetooth.from_address(args.ble_address), args.fetch_data_every_x_seconds)
