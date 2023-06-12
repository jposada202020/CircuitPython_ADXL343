# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT
"""
`adxl343`
================================================================================

MicroPython Driver for the Analog Devices ADXL343 Accelerometer


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

    _measurement_mode = RWBits(1, _POWER_CTL, 3)
    _resolution_mode = RWBits(1, _DATA_FORMAT, 3)
    _acceleration_range = RWBits(2, _DATA_FORMAT, 0)

    needed_info = UnaryStruct(_POWER_CTL, "B")

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
        Sensor measurement_mode

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
        Sensor Acceleration
        :return: Acceleration Data
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
        Sensor resolution_mode

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
