import argparse
import time

from genki_wave.data_organization import ButtonEvent
from genki_wave.discover import run_discover_bluetooth
from genki_wave.threading import ReaderThreadSerial, ReaderThreadBluetooth


def main(reader_thread):
    """A simple function to showcase reading from a thread. Fetches data every 0.1s"""

    with reader_thread as wave:
        last_time = None
        for _ in range(50):
            val = wave.queue.pop_all()
            if val:
                for v in val:
                    if isinstance(v, ButtonEvent):
                        print(v)
                print(val[-1])

            curr_time = time.time()
            if last_time is None:
                last_time = curr_time
            sleep_time = max(0.0, 0.1 - (last_time - curr_time))
            time.sleep(sleep_time)
            last_time = time.time()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--ble-address", type=str)
    parser.add_argument("--use-serial", action="store_true")
    args = parser.parse_args()

    if args.use_serial:
        main(ReaderThreadSerial.from_port())
    else:
        if args.ble_address is None:
            print("No bluetooth address (--ble-address) supplied, searching for devices...")
            run_discover_bluetooth()
        else:
            reader_thread = ReaderThreadBluetooth.from_address(args.ble_address)
            main(reader_thread)
