from enum import IntEnum


class PackageId(IntEnum):
    DATASTREAM = 1
    BATTERY_STATUS = 2
    DEVICE_INFO = 3
    BUTTON_EVENT = 4
    DEVICE_MODE = 5
    IDENTIFY = 6
    RECENTER = 7
    DISPLAY_FRAME = 8
    RAW_DATA = 9


class PackageType(IntEnum):
    REQUEST = 1
    RESPONSE = 2
    STREAM = 3


class DeviceMode(IntEnum):
    PRESET = 100
    SOFTWAVE = 101
    WAVEFRONT = 102
    API = 103


class ButtonId(IntEnum):
    """Which button is a package representing"""

    TOP = 0
    MIDDLE = 1
    BOTTOM = 2


class ButtonAction(IntEnum):
    """The action of a button package

    Up: button was released
    Down: button was pressed down
    Long: a long press was detected (button down for 500ms or more)
    LongUp: a long press was released (I think you'll always receive an "up" event with this one)
    ExtraLong: an extra long press was detected (I think it's about 2000ms, you'll always receive a "long" event
               before this one)
    ExtraLongUp: button released after an "extra long" press
    Click: button was pressed down and released "quickly" (i.e. not triggering a long press)
    DoubleClick: not used
    """

    UP = 0
    DOWN = 1
    LONG = 2
    LONGUP = 3
    EXTRALONG = 4
    EXTRALONGUP = 5
    CLICK = 6
    DOUBLECLICK = 7
