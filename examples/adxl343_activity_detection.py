# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import adxl343

i2c = board.I2C()
adx = adxl343.ADXL343(i2c)

adx.activity_threshold = 20  # m/s2
adx.activity_mode = adxl343.ACTIVITY_ENABLED

while True:
    print(f"Activity detected {adx.activity_detected}")
    time.sleep(0.5)
