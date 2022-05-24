import argparse
from pathlib import Path
import logging


from genki_wave.callbacks import ButtonAndDataPrint, CsvOutput
from genki_wave.asyncio_runner import run_asyncio_bluetooth, run_asyncio_serial
from genki_wave.discover import run_discover_bluetooth


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ble-address", type=str)
    parser.add_argument("--use-serial", action="store_true")
    parser.add_argument("--button", action="store_true", help="Handler that prints the button and the action")
    parser.add_argument(
        "--csv", type=str, default=None, help="Path to the output csv. If none is given no csv is written"
    )
    parser.add_argument("--log", type=str, default=None)
    args = parser.parse_args()
    log_level = getattr(logging, args.log.upper() if args.log else "WARNING", logging.WARNING)
    logging.basicConfig(format="%(levelname).4s:%(asctime)s [%(filename)s:%(lineno)d] - %(message)s ", level=log_level)

    callbacks = []
    if args.button:
        callbacks.append(ButtonAndDataPrint(5))
    if args.csv is not None:
        callbacks.append(CsvOutput(Path(args.csv)))

    if not callbacks:
        print("Warning: no callbacks supplied, the data received won't be processed in any way")

    if args.use_serial:
        run_asyncio_serial(callbacks)
    else:
        if args.ble_address is None:
            print("No bluetooth address (--ble-address) supplied, searching for devices...")
            run_discover_bluetooth()
        else:
            print("Turn off by holding the `TOP` button")
            run_asyncio_bluetooth(callbacks, args.ble_address)


if __name__ == "__main__":
    main()
