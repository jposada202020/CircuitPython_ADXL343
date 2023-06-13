# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`adxl343`
================================================================================

CircuitPython Driver for the Analog Devices ADXL343 Accelerometer


* Author(s): Jose D. Montoya


"""

from micropython import const
from adafruit_bus_device import i2c_device
from adafruit_register.i2c_struct import ROUnaryStruct, UnaryStruct, Struct
from adafruit_register.i2c_bits import RWBits

try:
    from busio import I2C
    from typing import Tuple
except ImportError:
    pass


__version__ = "0.0.0+auto.0"
__repo__ = "https://github.com/jposada202020/CircuitPython_ADXL343.git"

_STANDARD_GRAVITY = 9.80665
_REG_WHOAMI = const(0x00)
_POWER_CTL = const(0x2D)
_DATA_FORMAT = const(0x31)
_ACC = const(0x32)
_THRESH_TAP = const(0x1D)
_INT_ENABLE = const(0x2E)
_INT_SOURCE = const(0x30)
_TAP_AXES = const(0x2A)
_DUR = const(0x21)
_LATENT = const(0x22)
_WINDOW = const(0x23)

STANDBY = const(0b0)
READY = const(0b1)
measurement_mode_values = (STANDBY, READY)

LOW_RES = const(0b0)
HIGH_RES = const(0b1)
resolution_mode_values = (LOW_RES, HIGH_RES)

RANGE_2 = const(0b00)
RANGE_4 = const(0b01)
RANGE_8 = const(0b10)
RANGE_16 = const(0b11)
acceleration_range_values = (RANGE_2, RANGE_4, RANGE_8, RANGE_16)

ST_DISABLED = const(0b0)
ST_ENABLED = const(0b1)
single_tap_mode_values = (ST_DISABLED, ST_ENABLED)


class ADXL343:
    """Driver for the ADXL343 Sensor connected over I2C.

    :param ~busio.I2C i2c_bus: The I2C bus the ADXL343 is connected to.
    :param int address: The I2C device address. Defaults to :const:`0x53`

    :raises RuntimeError: if the sensor is not found

    **Quickstart: Importing and using the device**

    Here is an example of using the :class:`ADXL343` class.
    First you will need to import the libraries to use the sensor

    .. code-block:: python

        import board
        import adxl343

    Once this is done you can define your `board.I2C` object and define your sensor object

    .. code-block:: python

        i2c = board.I2C()  # uses board.SCL and board.SDA
        adxl = adxl343.ADXL343(i2c)

    Now you have access to the attributes

    .. code-block:: python

        accx, accy, accz = adxl.acceleration

    """

    _device_id = ROUnaryStruct(_REG_WHOAMI, "B")
    _acceleration_data = Struct(_ACC, "<hhh")
    _tap_threshold = UnaryStruct(_THRESH_TAP, "B")
    _tap_duration = UnaryStruct(_DUR, "B")
    _tap_latent = UnaryStruct(_LATENT, "B")
    _tap_window = UnaryStruct(_WINDOW, "B")

    _measurement_mode = RWBits(1, _POWER_CTL, 3)
    _resolution_mode = RWBits(1, _DATA_FORMAT, 3)
    _acceleration_range = RWBits(2, _DATA_FORMAT, 0)
    _single_tap_mode = RWBits(1, _INT_ENABLE, 6)
    _single_tap_mode_interrupt = RWBits(1, _INT_SOURCE, 6)
    _single_tap_enable_axes = RWBits(3, _TAP_AXES, 0)

    def __init__(self, i2c_bus: I2C, address: int = 0x53) -> None:
        self.i2c_device = i2c_device.I2CDevice(i2c_bus, address)

        if self._device_id != 0xE5:
            raise RuntimeError("Failed to find ADXL343")

        self._measurement_mode = True
        self._resolution_mode = True

        self._cached_resolution = 0.004

    @property
    def measurement_mode(self) -> str:
        """
        Sensor measurement_mode. Selecting 0 or `False` places the part
        into standby mode, and a setting of 1 or `True` places the part
        into measurement mode.
        The ADXL343 powers up in standby mode with minimum power
        consumption.

        +-----------------------------+-----------------+
        | Mode                        | Value           |
        +=============================+=================+
        | :py:const:`adxl343.STANDBY` | :py:const:`0b0` |
        +-----------------------------+-----------------+
        | :py:const:`adxl343.READY`   | :py:const:`0b1` |
        +-----------------------------+-----------------+
        """
        values = (
            "STANDBY",
            "READY",
        )
        return values[self._measurement_mode]

    @measurement_mode.setter
    def measurement_mode(self, value: int) -> None:
        if value not in measurement_mode_values:
            raise ValueError("Value must be a valid measurement_mode setting")
        self._measurement_mode = value

    @property
    def acceleration(self) -> Tuple[float, float, float]:
        """
        Acceleration Data in :math:`m / s ^ 2`
        """
        x, y, z = self._acceleration_data
        x = x * _STANDARD_GRAVITY * self._cached_resolution
        y = y * _STANDARD_GRAVITY * self._cached_resolution
        z = z * _STANDARD_GRAVITY * self._cached_resolution
        return x, y, z

    @property
    def acceleration_range(self) -> str:
        """
        Sensor acceleration_range

        +------------------------------+------------------+
        | Mode                         | Value            |
        +==============================+==================+
        | :py:const:`adxl343.RANGE_2`  | :py:const:`0b00` |
        +------------------------------+------------------+
        | :py:const:`adxl343.RANGE_4`  | :py:const:`0b01` |
        +------------------------------+------------------+
        | :py:const:`adxl343.RANGE_8`  | :py:const:`0b10` |
        +------------------------------+------------------+
        | :py:const:`adxl343.RANGE_16` | :py:const:`0b11` |
        +------------------------------+------------------+
        """
        values = ("RANGE_2", "RANGE_4", "RANGE_8", "RANGE_16")
        return values[self._acceleration_range]

    @acceleration_range.setter
    def acceleration_range(self, value: int) -> None:
        if value not in acceleration_range_values:
            raise ValueError("Value must be a valid acceleration_range setting")
        if self._resolution_mode == 0:
            res_values = {0: 0.004, 1: 0.008, 2: 0.016, 3: 0.031}
            self._cached_resolution = res_values[value]
        else:
            self._cached_resolution = 0.004

        self._acceleration_range = value

    @property
    def resolution_mode(self) -> str:
        """
        Sensor resolution_mode. When :attr:`resolution_mode` is set to `True`,
        the device is in full resolution mode, where the output resolution
        increases with the g range set by the range bits to maintain a 4
        mg/LSB scale factor. When is set to `False`, the device is in 10-bit
        mode, and the range bits determine the maximum g
        :attr:`acceleration_range` and scale factor.

        +------------------------------+-----------------+
        | Mode                         | Value           |
        +==============================+=================+
        | :py:const:`adxl343.LOW_RES`  | :py:const:`0b0` |
        +------------------------------+-----------------+
        | :py:const:`adxl343.HIGH_RES` | :py:const:`0b1` |
        +------------------------------+-----------------+
        """
        values = (
            "LOW_RES",
            "HIGH_RES",
        )
        return values[self._resolution_mode]

    @resolution_mode.setter
    def resolution_mode(self, value: int) -> None:
        if value not in resolution_mode_values:
            raise ValueError("Value must be a valid resolution_mode setting")
        self._resolution_mode = value
        if value == 0:
            res_values = {0: 0.004, 1: 0.008, 2: 0.016, 3: 0.031}
            self._cached_resolution = res_values[self._acceleration_range]
        else:
            self._cached_resolution = 0.004

    @property
    def tap_threshold(self) -> float:
        """
        Tap threshold in :math:`m / s ^ 2`
        :return:
        """
        return self._tap_threshold * 0.0627451 * _STANDARD_GRAVITY

    @tap_threshold.setter
    def tap_threshold(self, value: float) -> None:

        if 156 < value < 1:
            raise ValueError("Value should be a valid tap_threshold setting")
        self._tap_threshold = int(value / _STANDARD_GRAVITY / 0.0627451)

    @property
    def single_tap_mode(self) -> str:
        """
        Sensor single_tap_mode

        +---------------------------------+-----------------+
        | Mode                            | Value           |
        +=================================+=================+
        | :py:const:`adxl343.ST_DISABLED` | :py:const:`0b0` |
        +---------------------------------+-----------------+
        | :py:const:`adxl343.ST_ENABLED`  | :py:const:`0b1` |
        +---------------------------------+-----------------+
        """
        values = (
            "ST_DISABLED",
            "ST_ENABLED",
        )
        return values[self._single_tap_mode]

    @single_tap_mode.setter
    def single_tap_mode(self, value: int) -> None:
        if value not in single_tap_mode_values:
            raise ValueError("Value must be a valid single_tap_mode setting")
        self._single_tap_mode = value
        if value == 1:
            self._single_tap_enable_axes = 0b111
        else:
            self._single_tap_enable_axes = 0

    @property
    def single_tap_activated(self) -> bool:
        """
        Returns if a single tap event was detected
        :return: bool
        """
        values = {0: False, 1: True}
        return values[self._single_tap_mode_interrupt]

    @property
    def tap_duration(self) -> float:
        """
        Tap threshold in us. Maximum time that an event must be above the
        :attr:`tap_threshold` to qualify as a tap event. The scale factor
        is 625 μs/LSB.
        A value of 0 disables the single tap/ double tap functions

        """
        return self._tap_duration * 625

    @tap_duration.setter
    def tap_duration(self, value: int) -> None:
        if 159000 < value < 1:
            raise ValueError("Value should be a valid tap_duration setting")
        self._tap_duration = int(value / 625)

    @property
    def tap_latent(self) -> float:
        """
        Wwait time from the detection of a tap event to the
        start of the time window during which a possible second tap event can 
        be detected. The scale factor is 1.25 ms/LSB. 
        A value of 0 disables the double tap function.

        """
        return self._tap_latent * 1.25

    @tap_latent.setter
    def tap_latent(self, value: int) -> None:
        if 318 < value < 1:
            raise ValueError("Value should be a valid tap_latent setting")
        self._tap_latent = int(value / 1.25)

    @property
    def tap_window(self) -> float:
        """
        Time after the expiration of the latency time during which a
        second valid tap can begin. 
        The scale factor is 1.25 ms/LSB. 
        A value of 0 disables the double tap function

        """
        return self._tap_window * 1.25

    @tap_window.setter
    def tap_window(self, value: int) -> None:
        if 318 < value < 1:
            raise ValueError("Value should be a valid tap_window setting")
        self._tap_window = int(value / 1.25)
