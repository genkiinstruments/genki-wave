# Wave
This repository contains a simple Python API interface for [Wave by Genki](https://genkiinstruments.com/wave). The API provides easy access to Wave's onboard sensor data, as well as processed motion data using proprietary algorithms in a very small form factor. 

For more details, please refer to the [official documentation](https://www.notion.so/genkiinstruments/Wave-API-8a91bd3553ee4529878342dec477d93f).

# Installation
To install the package, clone the repository and use pip to install.

```bash
git clone git@github.com:genkiinstruments/genki-wave.git
cd genki-wave
python -m pip install .
```
or
```
python -m pip install -e .
```
If you want to change the code after installing

This package has been tested with `python 3.8`

## Setting up the Wave ring
Make sure you've installed the latest firmware on your Wave ring by following [these instructions](https://www.notion.so/genkiinstruments/Wave-Manual-Firmware-Update-87ce5d60ff94492dadcfe4c406192b5b).

The Wave ring is turned on by pressing the middle button once. To turn Wave off, hold the top and bottom buttons down for one second.

Refer to the [documentation](https://www.notion.so/genkiinstruments/Wave-API-8a91bd3553ee4529878342dec477d93f) for a detailed overview of how to use and interface with the API.

# Quickstart
## MIDI
The simplest way to start is to run `examples/run_midi.py`. That script does not depend on this library, only
`pygame`, and allows a user to interface with the ring through midi, if it is recognized by the operating system as a midi device.
If the midi data is not enough, then you can move on to the other scripts that output more data, and provide two-way communication with Wave.

## General

To get started using this package, install the dependencies and run any of the examples e.g.

```bash
python examples/run_asyncio.py
```

# Known issues
* When running via serial the Wave ring has to be turned off first, then connected and the script run
* When connected via bluetooth and the program is not turned off "properly" e.g. with a keyboard interrupt,
there is no proper cleanup that happens. Currently the only "clean" way is to hold the top button for a long time
