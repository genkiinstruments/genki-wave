# Wave
Python interface for the wave ring

# Installation
Currently the only way to install is to clone the repository and pip install from there

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

This package has only been tested in `python 3.8`

## Setting up the Wave ring
TODO

# Quickstart
## MIDI
The simplest way to start is to run `examples/run_midi.py`. That script does not depend on this library, only
`pygame`, and allows a user to interface with the ring as a midi device if it's connected as a midi device.
If the midi data is not enough, then you can move on to the other scripts that output more data.

## General
Install the dependencies and run any of the examples e.g.

```bash
python examples/run_asyncio.py
```
