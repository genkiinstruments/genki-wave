import abc
import csv
from pathlib import Path
from typing import Union, Optional, TextIO

from genki_wave.data import ButtonEvent, DataPackage


class WaveCallback(abc.ABC):
    @abc.abstractmethod
    def _button_handler(self, data: ButtonEvent) -> None:
        pass

    @abc.abstractmethod
    def _data_handler(self, data: DataPackage) -> None:
        pass

    def __call__(self, data: Union[ButtonEvent, DataPackage]) -> None:
        if isinstance(data, ButtonEvent):
            self._button_handler(data)
        elif isinstance(data, DataPackage):
            self._data_handler(data)
        else:
            raise ValueError(f"Got data of unexpected type {type(data)}")


class ButtonAndDataPrint(WaveCallback):
    """
    Callback that prints out all button presses received and prints a data package every `print_data_every_n_seconds`
    seconds. Useful for debugging and testing.

    Args:
        print_data_every_n_seconds: The interval to print a data package
    """

    def __init__(self, print_data_every_n_seconds: Optional[float] = None):
        self._last_time = None
        self._print_data_every_n_seconds = print_data_every_n_seconds

    def _button_handler(self, data: ButtonEvent) -> None:
        # We use `str` to force the `enum` to print the long version of the name e.g. `ButtonId.MIDDLE` instead of `1`
        print(f"Button: {str(data.button_id)}, Action: {str(data.action)}")

    def _data_handler(self, data: DataPackage) -> None:
        """If there are more than `_print_data_every_n_seconds` seconds since something was printed out, print it"""
        if self._print_data_every_n_seconds is None:
            return

        if self._last_time is None:
            self._last_time = data.timestamp_us

        if (data.timestamp_us - self._last_time) > self._print_data_every_n_seconds * 10**6:  # s to us
            print(data)
            self._last_time = data.timestamp_us


class CsvOutput(WaveCallback):
    """
    Exports the streaming data to a csv file, flushing it to the file every `flush_len` elements

    Default behaviour is to append the data if a file already exists

    Args:
        filename: The file the data will be exported to
        flush_len: How many samples to buffer before writing to a file
    """

    def __init__(self, filename: Path, flush_len: int = 256):

        self._events = []
        self._filename = filename
        self._fieldnames = DataPackage.flat_keys()
        self._flush_len = flush_len

        if not self._filename.exists():
            with open(self._filename, "w") as f:
                writer = self._get_writer(f)
                writer.writeheader()

    def _get_writer(self, f: TextIO) -> csv.DictWriter:
        return csv.DictWriter(f, fieldnames=self._fieldnames)

    def _reset_state(self) -> None:
        self._events = []

    def _button_handler(self, data: ButtonEvent) -> None:
        pass

    def _data_handler(self, data: DataPackage) -> None:
        """Receives the data and writes it out if enough data points have been collected"""
        self._events.append(data)

        if len(self._events) < self._flush_len:
            return

        with open(self._filename, "a") as f:
            writer = self._get_writer(f)

            for event in self._events:
                d = event.as_flat_dict()
                assert set(d.keys()) == set(writer.fieldnames), "Expected event.fieldnames == writer.fieldnames"
                writer.writerow(d)

        self._reset_state()
