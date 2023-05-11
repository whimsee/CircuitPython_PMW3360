# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jerico Tenmatay
#
# SPDX-License-Identifier: Unlicense

import PMW3360
import board
from digitalio import DigitalInOut, Direction

def delta(value):
if value & 0x8000:
    return -(~value & 0x7fff)
else:
    return value & 0x7fff

sensor = PMW3360.PMW3360(board.CLK, board.MOSI, board.MISO, board.D10)

mt_pin = DigitalInOut(board.A0)
mt_pin.direction = Direction.INPUT

sensor.begin()

while True:

    data = sensor.read_burst()

    dx = delta(data["dx"])
    dy = delta(data["dy"])

    if mt_pin.value == 0:
    print(dx)
    print(dy)
    print("")