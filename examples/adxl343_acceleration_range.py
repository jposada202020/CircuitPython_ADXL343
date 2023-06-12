# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import adxl343

i2c = board.I2C()
adx = adxl343.ADXL343(i2c)

adx.acceleration_range = adxl343.RANGE_16

while True:
    for acceleration_range in adxl343.acceleration_range_values:
        print("Current Acceleration range setting: ", adx.acceleration_range)
        for _ in range(10):
            accx, accy, accz = adx.acceleration
            print("x:{:.2f}m/s2, y:{:.2f}m/s2, z:{:.2f}m/s2".format(accx, accy, accz))
            time.sleep(0.5)
        adx.acceleration_range = acceleration_range
