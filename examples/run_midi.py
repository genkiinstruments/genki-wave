"""
This script is adopted from [here](https://github.com/atizo/pygame/blob/master/examples/midi.py)

# MacOS and Windows

Connecting the wave ring as a midi device via bluetooth should work out-of-the-box on Windows and MacOS.

# Linux
On Linux you might need to re-install `BlueZ` with support for midi as follows.
Installation instructions for Linux. Taken from
[here](https://tttapa.github.io/Pages/Ubuntu/Software-Installation/BlueZ.html)

```
sudo apt install libudev-dev libical-dev libreadline-dev libdbus-1-dev libasound2-dev
sudo apt install build-essential

# Use whatever version of BlueZ you want and change accordingly
cd /tmp
wget https://mirrors.edge.kernel.org/pub/linux/bluetooth/bluez-5.53.tar.xz
tar -xf bluez-5.53.tar.xz

cd bluez-5.53
./configure --enable-midi --with-systemdsystemunitdir=/etc/systemd/system
make
sudo make install
sudo apt-get install --reinstall bluez
```

You might need a restart after this step

Check if the device is detected:
```
aconnect -lio
```

If pygame raises a warning that `Cannot open shared library libasound_module_conf_pulse.so` it might be searching
in the wrong place a way to fix it is to create a symbolic link to where the actual library is to where pygame searches.
An example for ubuntu (pygame searches in `/usr/lib/alsa-lib`)
sudo ln -s /usr/lib/x86_64-linux-gnu/alsa-lib /usr/lib/alsa-lib

Solution adapted from [here](https://stackoverflow.com/questions/57946421/im-trying-to-run-this-code-initialize-pygame-midi-code-but-it-returns-an-error)  # noqa
"""
import functools
from enum import IntEnum
from typing import Optional, Tuple

try:
    import pygame
    import pygame.midi
except ModuleNotFoundError:
    raise ModuleNotFoundError(
        "This script only depends on pygame, not the genki-wave library so please install 'pygame'"
        "manually to run this script"
    )


class MidiStatus(IntEnum):
    DATA = 176


class Movements(IntEnum):
    PITCH = 16
    YAW = 17
    ROLL = 18


movements_values = [item.value for item in Movements]


def midi_setup_and_teardown(func):
    """Sets up midi before calling a function and tears it down after running

    Alternatively `pygame.midi.init()` and `pygame.midi.quit()` can be called at the beginning and end of each
    function manually
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        pygame.midi.init()
        results = func(*args, **kwargs)
        pygame.midi.quit()
        return results

    return wrapper


@midi_setup_and_teardown
def print_device_info():
    """Prints all midi devices that were found"""
    for i in range(pygame.midi.get_count()):
        interf, name, is_input, output, opened = pygame.midi.get_device_info(i)

        in_out = ""
        if is_input:
            in_out = "(input)"
        if output:
            in_out = "(output)"

        print(f"{i}: interface {interf}, name {name}, opened {opened} {in_out}")


@midi_setup_and_teardown
def wave_input_device_info() -> Optional[Tuple[int, str]]:
    """Automatically find input `Wave` input device"""
    result = None
    for i in range(pygame.midi.get_count()):
        interf, name, is_input, output, opened = pygame.midi.get_device_info(i)

        name_decoded = name.decode()
        if is_input and "Wave" in name_decoded:
            result = i, name_decoded
    return result


@midi_setup_and_teardown
def input_main(device_id):
    pygame.init()
    # Define our input device
    input_midi = pygame.midi.Input(device_id)
    pygame.display.set_mode((1, 1))
    going = True
    print_vals_results = ["", "", ""]

    while going:
        for event in pygame.event.get():
            if event.type in [pygame.QUIT]:
                going = False
            if event.type in [pygame.KEYDOWN]:
                # Program will stop if any button is pressed
                going = False
            if event.type in [pygame.midi.MIDIIN, pygame.USEREVENT]:
                print(event)

        # Check if there is any data in the buffer of the midi-device. If not, continue with the loop
        if not input_midi.poll():
            continue

        # Read all the data from the midi buffer (max_size=1024)
        midi_events = input_midi.read(1024)
        midi_events = pygame.midi.midis2events(midi_events, input_midi.device_id)

        # 3 different functions to use. Uncomment different ones to try out
        # post_custom_events(midi_events)
        # post_midi_events(midi_events, Movements.ROLL)
        print_vals_results = print_values(midi_events, print_vals_results)

    del input_midi


def print_values(midi_events, previous_vals: list) -> list:
    """Prints a 'data' midi event i.e. where there is information sent about roll/pitch/yaw

    If an event of a certain type is not found, prints the last value for that event
    """
    s = previous_vals
    for m_e in midi_events:
        if m_e.status == MidiStatus.DATA and m_e.data1 in movements_values:
            s = [m_e.data2 if m_e.data1 == val else prev_val for prev_val, val in zip(previous_vals, movements_values)]
    print(f"P: {s[0]:>3}, Y: {s[1]:>3}, R: {s[2]:>3}")
    return s


def post_custom_events(midi_events):
    """Only print certain events"""
    for m_e in midi_events:
        if m_e.status == MidiStatus.DATA and m_e.data1 == Movements.YAW:
            if m_e.data2 > 100:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"val": "down"}))
            if m_e.data2 < 30:
                pygame.event.post(pygame.event.Event(pygame.USEREVENT, {"val": "up"}))


def post_midi_events(midi_events, movement_type):
    """Post all midi events corresponding to data coming in"""
    for m_e in midi_events:
        if m_e.status == MidiStatus.DATA and m_e.data1 == movement_type:
            pygame.event.post(m_e)


def main():
    print("Make sure your Wave is connected to your computer as a midi device")
    print_device_info()
    device_id, name = wave_input_device_info()
    if device_id is not None:
        print(f"Found input device: {name} - {device_id}")
        print("Press any keyboard button to stop")
        input_main(device_id)
    else:
        print("Did not find a Wave device")


if __name__ == "__main__":
    main()
