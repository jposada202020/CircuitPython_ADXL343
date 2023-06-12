# SPDX-FileCopyrightText: Copyright (c) 2023 Jose D. Montoya
#
# SPDX-License-Identifier: MIT

import time
import board
import adxl343

i2c = board.I2C()  # uses board.SCL and board.SDA
adx = adxl343.ADXL343(i2c)

while True:
    # print("Pressure: {:.2f}hPa".format(lps.pressure))
    time.sleep(0.5)
