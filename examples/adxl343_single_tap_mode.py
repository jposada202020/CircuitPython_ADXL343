# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import adxl343

i2c = board.I2C()
adx = adxl343.ADXL343(i2c)

adx.single_tap_mode = adxl343.ST_ENABLED

adx.tap_threshold = 4  # m/s2
adx.tap_duration = 625  # us

while True:
    print(f"Single Tap detected {adx.single_tap_activated}")
    time.sleep(0.5)
