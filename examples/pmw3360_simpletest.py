# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jerico Tenmatay
#
# SPDX-License-Identifier: Unlicense

import PMW3360
import board
from digitalio import DigitalInOut, Direction

# Normalizes the value into a signed value.
def delta(value):
# Negative if MSB is 1
if value & 0x8000:
    return -(~value & 0x7fff)
else:
    return value & 0x7fff

# board.SCK may be board.CLK depending on the board
sensor = PMW3360.PMW3360(board.SCK, board.MOSI, board.MISO, board.D10)

# Pin goes low if there is motion
mt_pin = DigitalInOut(board.A0)
mt_pin.direction = Direction.INPUT

# Initalizes the sensor
sensor.begin()

while True:
    # Captures a snapshot
    data = sensor.read_burst()

    dx = delta(data["dx"])
    dy = delta(data["dy"])
    
    # uncomment if mt_pin isn't used 
    # if data["isOnSurface"] == True and data["isMotion"] and mt_pin.value == True:

    if mt_pin.value == 0:
    print(dx)
    print(dy)
    print("")
