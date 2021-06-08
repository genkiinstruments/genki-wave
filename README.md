# Wave
This repository contains a simple Python API interface for [Wave by Genki](https://genkiinstruments.com/wave).
The API provides easy access to Wave's onboard sensor data, as well as processed motion data using proprietary
algorithms in a very small form factor. 

For more details, please refer to the
[official documentation](https://www.notion.so/genkiinstruments/Wave-API-8a91bd3553ee4529878342dec477d93f).

# Installation
This package has been tested with `python 3.8`

## MacOs
To install the package, pip install:
```
python -m pip install genki-wave
```

## Linux
If it is not pre-installed, you need to install [bluez](http://www.bluez.org/).

To install the package, pip install:
```
python -m pip install genki-wave
```

## Setting up the Wave ring
Make sure you've installed the latest firmware on your Wave ring by following
[these instructions](https://www.notion.so/genkiinstruments/Wave-Manual-Firmware-Update-87ce5d60ff94492dadcfe4c406192b5b).

The Wave ring is turned on by pressing the middle button once. To turn Wave off, hold the top and bottom buttons
down for one second.

Refer to the [documentation](https://www.notion.so/genkiinstruments/Wave-API-8a91bd3553ee4529878342dec477d93f)
for a detailed overview of how to use and interface with the API.

# Quickstart
## General
Turn on the Wave ring, make sure it is not connected to any device and run

```python
from genki_wave.discover import run_discover_bluetooth

run_discover_bluetooth()
```
to find the address and then run

```python
from genki_wave.asyncio import run_asyncio_bluetooth
from genki_wave.callbacks import ButtonAndDataPrint

callbacks = [ButtonAndDataPrint(print_data_every_n_seconds=5)]
ble_address = ""  # Address of the Wave ring, found in the previous step
run_asyncio_bluetooth(callbacks, ble_address)
```
this uses a simple callback that prints out which button has been pressed, and a package of data every 5 seconds

To see other examples, run the scripts in `genki_wave/examples`

## MIDI
One of the simplest way to start is to run `examples/run_midi.py`. That script does not depend on this library, only
`pygame`, and allows a user to interface with the ring through midi, if it is recognized by the operating system as a
midi device. If the midi data is not enough, then you can move on to the other scripts that output more data, and
provide two-way communication with Wave.

# Known issues
* The python bluetooth library, [bleak](https://github.com/hbldh/bleak), can only connect to devices that are not
  connected to the computer. After pairing Wave to a Ubuntu machine, the ring tends to connect automatically quite
  aggressively and when that happens can not be accessed via bleak. One "solution" is to use `bluetoothctl`
* When running via serial the Wave ring has to be turned off first, then connected and the script run
* When connected via bluetooth using asyncio (not threads) and the program is not turned off "properly" e.g. with a
  keyboard interrupt, there is no proper cleanup that happens for the bluetooth connection. Currently the only "clean"
  way is to use the hard-coded method, by holding the top button for a few seconds while the program is running
