# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jerico Tenmatay
#
# SPDX-License-Identifier: Unlicense

import PMW3360
import board
from digitalio import DigitalInOut, Direction

# board.SCK may be board.CLK depending on the board
# board.D10 is the cs pin
sensor = PMW3360.PMW3360(board.SCK, board.MOSI, board.MISO, board.D10)

# Any pin. Goes LOW if motion is detected.
mt_pin = DigitalInOut(board.A0)
mt_pin.direction = Direction.INPUT

# Initalizes the sensor
sensor.begin()

while True:
    # Captures a snapshot
    data = sensor.read_burst()
    
    # uncomment if mt_pin isn't used 
    # if data["is_on_surface"] == True and data["is_motion"] and mt_pin.value == True:
    if mt_pin.value == 0:
        print(data)
