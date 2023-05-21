# SPDX-FileCopyrightText: 2017 Scott Shawcroft, written for Adafruit Industries
# SPDX-FileCopyrightText: Copyright (c) 2023 Jerico Tenmatay
#
# SPDX-License-Identifier: MIT
"""
`pmw3360`
================================================================================

CircuitPython library for the PMW3360 motion sensor.
Port of Arduino PMW3360 Module Library by SunjunKim

* Author(s): Jerico Tenmatay

Implementation Notes
--------------------

**Hardware:**

* PMW3360

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

* Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice

"""

# imports
import time
import board
import busio
import micropython
from digitalio import DigitalInOut, Direction, Pull
from adafruit_bus_device.spi_device import SPIDevice

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/whimsee/CircuitPython_PMW3360.git"

_REG_Product_ID                           = const(0x00)
_REG_Revision_ID                          = const(0x01)
_REG_Motion                               = const(0x02)
_REG_Delta_X_L                            = const(0x03)
_REG_Delta_X_H                            = const(0x04)
_REG_Delta_Y_L                            = const(0x05)
_REG_Delta_Y_H                            = const(0x06)
_REG_SQUAL                                = const(0x07)
_REG_Raw_Data_Sum                         = const(0x08)
_REG_Maximum_Raw_data                     = const(0x09)
_REG_Minimum_Raw_data                     = const(0x0A)
_REG_Shutter_Lower                        = const(0x0B)
_REG_Shutter_Upper                        = const(0x0C)
_REG_Control                              = const(0x0D)
_REG_Config1                              = const(0x0F)
_REG_Config2                              = const(0x10)
_REG_Angle_Tune                           = const(0x11)
_REG_Frame_Capture                        = const(0x12)
_REG_SROM_Enable                          = const(0x13)
_REG_Run_Downshift                        = const(0x14)
_REG_Rest1_Rate_Lower                     = const(0x15)
_REG_Rest1_Rate_Upper                     = const(0x16)
_REG_Rest1_Downshift                      = const(0x17)
_REG_Rest2_Rate_Lower                     = const(0x18)
_REG_Rest2_Rate_Upper                     = const(0x19)
_REG_Rest2_Downshift                      = const(0x1A)
_REG_Rest3_Rate_Lower                     = const(0x1B)
_REG_Rest3_Rate_Upper                     = const(0x1C)
_REG_Observation                          = const(0x24)
_REG_Data_Out_Lower                       = const(0x25)
_REG_Data_Out_Upper                       = const(0x26)
_REG_Raw_Data_Dump                        = const(0x29)
_REG_SROM_ID                              = const(0x2A)
_REG_Min_SQ_Run                           = const(0x2B)
_REG_Raw_Data_Threshold                   = const(0x2C)
_REG_Config5                              = const(0x2F)
_REG_Power_Up_Reset                       = const(0x3A)
_REG_Shutdown                             = const(0x3B)
_REG_Inverse_Product_ID                   = const(0x3F)
_REG_LiftCutoff_Tune3                     = const(0x41)
_REG_Angle_Snap                           = const(0x42)
_REG_LiftCutoff_Tune1                     = const(0x4A)
_REG_Motion_Burst                         = const(0x50)
_REG_LiftCutoff_Tune_Timeout              = const(0x58)
_REG_LiftCutoff_Tune_Min_Length           = const(0x5A)
_REG_SROM_Load_Burst                      = const(0x62)
_REG_Lift_Config                          = const(0x63)
_REG_Raw_Data_Burst                       = const(0x64)
_REG_LiftCutoff_Tune2                     = const(0x65)

# Break up firmware data to not exhaust the pystack
_FIRMWARE_DATA_1 = bytearray(
    b"\x01\x04\x8e\x96\x6e\x77\x3e\xfe\x7e\x5f\x1d\xb8\xf2\x66\x4e"
    b"\xff\x5d\x19\xb0\xc2\x04\x69\x54\x2a\xd6\x2e\xbf\xdd\x19\xb0"
    b"\xc3\xe5\x29\xb1\xe0\x23\xa5\xa9\xb1\xc1\x00\x82\x67\x4c\x1a"
    b"\x97\x8d\x79\x51\x20\xc7\x06\x8e\x7c\x7c\x7a\x76\x4f\xfd\x59"
    b"\x30\xe2\x46\x0e\x9e\xbe\xdf\x1d\x99\x91\xa0\xa5\xa1\xa9\xd0"
    b"\x22\xc6\xef\x5c\x1b\x95\x89\x90\xa2\xa7\xcc\xfb\x55\x28\xb3"
    b"\xe4\x4a\xf7\x6c\x3b\xf4\x6a\x56\x2e\xde\x1f\x9d\xb8\xd3\x05"
    b"\x88\x92\xa6\xce\x1e\xbe\xdf\x1d\x99\xb0\xe2\x46\xef\x5c\x07"
    b"\x11\x5d\x98\x0b\x9d\x94\x97\xee\x4e\x45\x33\x6b\x44\xc7\x29"
    b"\x56\x27\x30\xc6\xa7\xd5\xf2\x56\xdf\xb4\x38\x62\xcb\xa0\xb6"
    b"\xe3\x0f\x84\x06\x24\x05\x65\x6f\x76\x89\xb5\x77\x41\x27\x82"
    b"\x66\x65\x82\xcc\xd5\xe6\x20\xd5\x27\x17\xc5\xf8\x03\x23\x7c"
    b"\x5f\x64\xa5\x1d\xc1\xd6\x36\xcb\x4c\xd4\xdb\x66\xd7\x8b\xb1"
    b"\x99\x7e\x6f\x4c\x36\x40\x06\xd6\xeb\xd7\xa2\xe4\xf4\x95\x51"
    b"\x5a\x54\x96\xd5\x53\x44\xd7\x8c\xe0\xb9\x40\x68\xd2\x18\xe9"
    b"\xdd\x9a\x23\x92\x48\xee\x7f\x43\xaf\xea\x77\x38\x84\x8c\x0a"
    b"\x72\xaf\x69\xf8\xdd\xf1\x24\x83\xa3\xf8\x4a\xbf\xf5\x94\x13"
    b"\xdb\xbb\xd8\xb4\xb3\xa0\xfb\x45\x50\x60\x30\x59\x12\x31\x71"
    b"\xa2\xd3\x13\xe7\xfa\xe7\xce\x0f\x63\x15\x0b\x6b\x94\xbb\x37"
    b"\x83\x26\x05\x9d\xfb\x46\x92\xfc\x0a\x15\xd1\x0d\x73\x92\xd6"
    b"\x8c\x1b\x8c\xb8\x55\x8a\xce\xbd\xfe\x8e\xfc\xed\x09\x12\x83"
    b"\x91\x82\x51\x31\x23\xfb\xb4\x0c\x76\xad\x7c\xd9\xb4\x4b\xb2"
    b"\x67\x14\x09\x9c\x7f\x0c\x18\xba\x3b\xd6\x8e\x14\x2a\xe4\x1b"
)

_FIRMWARE_DATA_2 = bytearray(
    b"\x52\x9f\x2b\x7d\xe1\xfb\x6a\x33\x02\xfa\xac\x5a\xf2\x3e\x88"
    b"\x7e\xae\xd1\xf3\x78\xe8\x05\xd1\xe3\xdc\x21\xf6\xe1\x9a\xbd"
    b"\x17\x0e\xd9\x46\x9b\x88\x03\xea\xf6\x66\xbe\x0e\x1b\x50\x49"
    b"\x96\x40\x97\xf1\xf1\xe4\x80\xa6\x6e\xe8\x77\x34\xbf\x29\x40"
    b"\x44\xc2\xff\x4e\x98\xd3\x9c\xa3\x32\x2b\x76\x51\x04\x09\xe7" 
    b"\xa9\xd1\xa6\x32\xb1\x23\x53\xe2\x47\xab\xd6\xf5\x69\x5c\x3e" 
    b"\x5f\xfa\xae\x45\x20\xe5\xd2\x44\xff\x39\x32\x6d\xfd\x27\x57" 
    b"\x5c\xfd\xf0\xde\xc1\xb5\x99\xe5\xf5\x1c\x77\x01\x75\xc5\x6d" 
    b"\x58\x92\xf2\xb2\x47\x00\x01\x26\x96\x7a\x30\xff\xb7\xf0\xef" 
    b"\x77\xc1\x8a\x5d\xdc\xc0\xd1\x29\x30\x1e\x77\x38\x7a\x94\xf1" 
    b"\xb8\x7a\x7e\xef\xa4\xd1\xac\x31\x4a\xf2\x5d\x64\x3d\xb2\xe2" 
    b"\xf0\x08\x99\xfc\x70\xee\x24\xa7\x7e\xee\x1e\x20\x69\x7d\x44" 
    b"\xbf\x87\x42\xdf\x88\x3b\x0c\xda\x42\xc9\x04\xf9\x45\x50\xfc" 
    b"\x83\x8f\x11\x6a\x72\xbc\x99\x95\xf0\xac\x3d\xa7\x3b\xcd\x1c" 
    b"\xe2\x88\x79\x37\x11\x5f\x39\x89\x95\x0a\x16\x84\x7a\xf6\x8a" 
    b"\xa4\x28\xe4\xed\x83\x80\x3b\xb1\x23\xa5\x03\x10\xf4\x66\xea" 
    b"\xbb\x0c\x0f\xc5\xec\x6c\x69\xc5\xd3\x24\xab\xd4\x2a\xb7\x99" 
    b"\x88\x76\x08\xa0\xa8\x95\x7c\xd8\x38\x6d\xcd\x59\x02\x51\x4b" 
    b"\xf1\xb5\x2b\x50\xe3\xb6\xbd\xd0\x72\xcf\x9e\xfd\x6e\xbb\x44" 
    b"\xc8\x24\x8a\x77\x18\x8a\x13\x06\xef\x97\x7d\xfa\x81\xf0\x31" 
    b"\xe6\xfa\x77\xed\x31\x06\x31\x5b\x54\x8a\x9f\x30\x68\xdb\xe2" 
    b"\x40\xf8\x4e\x73\xfa\xab\x74\x8b\x10\x58\x13\xdc\xd2\xe6\x78" 
    b"\xd1\x32\x2e\x8a\x9f\x2c\x58\x06\x48\x27\xc5\xa9\x5e\x81\x47"
)

_FIRMWARE_DATA_3 = bytearray(
    b"\x89\x46\x21\x91\x03\x70\xa4\x3e\x88\x9c\xda\x33\x0a\xce\xbc"
    b"\x8b\x8e\xcf\x9f\xd3\x71\x80\x43\xcf\x6b\xa9\x51\x83\x76\x30"
    b"\x82\xc5\x6a\x85\x39\x11\x50\x1a\x82\xdc\x1e\x1c\xd5\x7d\xa9" 
    b"\x71\x99\x33\x47\x19\x97\xb3\x5a\xb1\xdf\xed\xa4\xf2\xe6\x26"
    b"\x84\xa2\x28\x9a\x9e\xdf\xa6\x6a\xf4\xd6\xfc\x2e\x5b\x9d\x1a"
    b"\x2a\x27\x68\xfb\xc1\x83\x21\x4b\x90\xe0\x36\xdd\x5b\x31\x42"
    b"\x55\xa0\x13\xf7\xd0\x89\x53\x71\x99\x57\x09\x29\xc5\xf3\x21"
    b"\xf8\x37\x2f\x40\xf3\xd4\xaf\x16\x08\x36\x02\xfc\x77\xc5\x8b"
    b"\x04\x90\x56\xb9\xc9\x67\x9a\x99\xe8\x00\xd3\x86\xff\x97\x2d"
    b"\x08\xe9\xb7\xb3\x91\xbc\xdf\x45\xc6\xed\x0f\x8c\x4c\x1e\xe6"
    b"\x5b\x6e\x38\x30\xe4\xaa\xe3\x95\xde\xb9\xe4\x9a\xf5\xb2\x55"
    b"\x9a\x87\x9b\xf6\x6a\xb2\xf2\x77\x9a\x31\xf4\x7a\x31\xd1\x1d"
    b"\x04\xc0\x7c\x32\xa2\x9e\x9a\xf5\x62\xf8\x27\x8d\xbf\x51\xff"
    b"\xd3\xdf\x64\x37\x3f\x2a\x6f\x76\x3a\x7d\x77\x06\x9e\x77\x7f"
    b"\x5e\xeb\x32\x51\xf9\x16\x66\x9a\x09\xf3\xb0\x08\xa4\x70\x96"
    b"\x46\x30\xff\xda\x4f\xe9\x1b\xed\x8d\xf8\x74\x1f\x31\x92\xb3"
    b"\x73\x17\x36\xdb\x91\x30\xd6\x88\x55\x6b\x34\x77\x87\x7a\xe7"
    b"\xee\x06\xc6\x1c\x8c\x19\x0c\x48\x46\x23\x5e\x9c\x07\x5c\xbf"
    b"\xb4\x7e\xd6\x4f\x74\x9c\xe2\xc5\x50\x8b\xc5\x8b\x15\x90\x60"
    b"\x62\x57\x29\xd0\x13\x43\xa1\x80\x88\x91\x00\x44\xc7\x4d\x19"
    b"\x86\xcc\x2f\x2a\x75\x5a\xfc\xeb\x97\x2a\x70\xe3\x78\xd8\x91"
    b"\xb0\x4f\x99\x07\xa3\x95\xea\x24\x21\xd5\xde\x51\x20\x93\x27"
    b"\x0a\x30\x73\xa8\xff\x8a\x97\xe9\xa7\x6a\x8e\x0d\xe8\xf0\xdf"
)

_FIRMWARE_DATA_4 = bytearray(
    b"\xec\xea\xb4\x6c\x1d\x39\x2a\x62\x2d\x3d\x5a\x8b\x65\xf8\x90"
    b"\x05\x2e\x7e\x91\x2c\x78\xef\x8e\x7a\xc1\x2f\xac\x78\xee\xaf" 
    b"\x28\x45\x06\x4c\x26\xaf\x3b\xa2\xdb\xa3\x93\x06\xb5\x3c\xa5" 
    b"\xd8\xee\x8f\xaf\x25\xcc\x3f\x85\x68\x48\xa9\x62\xcc\x97\x8f" 
    b"\x7f\x2a\xea\xe0\x15\x0a\xad\x62\x07\xbd\x45\xf8\x41\xd8\x36" 
    b"\xcb\x4c\xdb\x6e\xe6\x3a\xe7\xda\x15\xe9\x29\x1e\x12\x10\xa0" 
    b"\x14\x2c\x0e\x3d\xf4\xbf\x39\x41\x92\x75\x0b\x25\x7b\xa3\xce" 
    b"\x39\x9c\x15\x64\xc8\xfa\x3d\xef\x73\x27\xfe\x26\x2e\xce\xda" 
    b"\x6e\xfd\x71\x8e\xdd\xfe\x76\xee\xdc\x12\x5c\x02\xc5\x3a\x4e" 
    b"\x4e\x4f\xbf\xca\x40\x15\xc7\x6e\x8d\x41\xf1\x10\xe0\x4f\x7e" 
    b"\x97\x7f\x1c\xae\x47\x8e\x6b\xb1\x25\x31\xb0\x73\xc7\x1b\x97" 
    b"\x79\xf9\x80\xd3\x66\x22\x30\x07\x74\x1e\xe4\xd0\x80\x21\xd6" 
    b"\xee\x6b\x6c\x4f\xbf\xf5\xb7\xd9\x09\x87\x2f\xa9\x14\xbe\x27" 
    b"\xd9\x72\x50\x01\xd4\x13\x73\xa6\xa7\x51\x02\x75\x25\xe1\xb3" 
    b"\x45\x34\x7d\xa8\x8e\xeb\xf3\x16\x49\xcb\x4f\x8c\xa1\xb9\x36" 
    b"\x85\x39\x75\x5d\x08\x00\xae\xeb\xf6\xea\xd7\x13\x3a\x21\x5a" 
    b"\x5f\x30\x84\x52\x26\x95\xc9\x14\xf2\x57\x55\x6b\xb1\x10\xc2" 
    b"\xe1\xbd\x3b\x51\xc0\xb7\x55\x4c\x71\x12\x26\xc7\x0d\xf9\x51" 
    b"\xa4\x38\x02\x05\x7f\xb8\xf1\x72\x4b\xbf\x71\x89\x14\xf3\x77" 
    b"\x38\xd9\x71\x24\xf3\x00\x11\xa1\xd8\xd4\x69\x27\x08\x37\x35" 
    b"\xc9\x11\x9d\x90\x1c\x0e\xe7\x1c\xff\x2d\x1e\xe8\x92\xe1\x18" 
    b"\x10\x95\x7c\xe0\x80\xf4\x96\x43\x21\xf9\x75\x21\x64\x38\xdd" 
    b"\x9f\x1e\x95\x16\xda\x56\x1d\x4f\x9a\x53\xb2\xe2\xe4\x18\xcb"
)

_FIRMWARE_DATA_5 = bytearray(
    b"\x6b\x1a\x65\xeb\x56\xc6\x3b\xe5\xfe\xd8\x26\x3f\x3a\x84\x59" 
    b"\x72\x66\xa2\xf3\x75\xff\xfb\x60\xb3\x22\xad\x3f\x2d\x6b\xf9" 
    b"\xeb\xea\x05\x7c\xd8\x8f\x6d\x2c\x98\x9e\x2b\x93\xf1\x5e\x46" 
    b"\xf0\x87\x49\x29\x73\x68\xd7\x7f\xf9\xf0\xe5\x7d\xdb\x1d\x75" 
    b"\x19\xf3\xc4\x58\x9b\x17\x88\xa8\x92\xe0\xbe\xbd\x8b\x1d\x8d" 
    b"\x9f\x56\x76\xad\xaf\x29\xe2\xd9\xd5\x52\xf6\xb5\x56\x35\x57" 
    b"\x3a\xc8\xe1\x56\x43\x19\x94\xd3\x04\x9b\x6d\x35\xd8\x0b\x5f" 
    b"\x4d\x19\x8e\xec\xfa\x64\x91\x0a\x72\x20\x2b\xbc\x1a\x4a\xfe" 
    b"\x8b\xfd\xbb\xed\x1b\x23\xea\xad\x72\x82\xa1\x29\x99\x71\xbd" 
    b"\xf0\x95\xc1\x03\xdd\x7b\xc2\xb2\x3c\x28\x54\xd3\x68\xa4\x72" 
    b"\xc8\x66\x96\xe0\xd1\xd8\x7f\xf8\xd1\x26\x2b\xf7\xad\xba\x55" 
    b"\xca\x15\xb9\x32\xc3\xe5\x88\x97\x8e\x5c\xfb\x92\x25\x8b\xbf" 
    b"\xa2\x45\x55\x7a\xa7\x6f\x8b\x57\x5b\xcf\x0e\xcb\x1d\xfb\x20" 
    b"\x82\x77\xa8\x8c\xcc\x16\xce\x1d\xfa\xde\xcc\x0b\x62\xfe\xcc" 
    b"\xe1\xb7\xf0\xc3\x81\x64\x73\x40\xa0\xc2\x4d\x89\x11\x75\x33" 
    b"\x55\x33\x8d\xe8\x4a\xfd\xea\x6e\x30\x0b\xd7\x31\x2c\xde\x47" 
    b"\xe3\xbf\xf8\x55\x42\xe2\x7f\x59\xe5\x17\xef\x99\x34\x69\x91" 
    b"\xb1\x23\x8e\x20\x87\x2d\xa8\xfe\xd5\x8a\xf3\x84\x3a\xf0\x37" 
    b"\xe4\x09\x00\x54\xee\x67\x49\x93\xe4\x81\x70\xe3\x90\x4d\xef" 
    b"\xfe\x41\xb7\x99\x7b\xc1\x83\xba\x62\x12\x6f\x7d\xde\x6b\xaf" 
    b"\xda\x16\xf9\x55\x51\xee\xa6\x0c\x2b\x02\xa3\xfd\x8d\xfb\x30" 
    b"\x17\xe4\x6f\xdf\x36\x71\xc4\xca\x87\x25\x48\xb0\x47\xec\xea" 
    b"\xb4\xbf\xa5\x4d\x9b\x9f\x02\x93\xc4\xe3\xe4\xe8\x42\x2d\x68"
)

_FIRMWARE_DATA_6 = bytearray(
    b"\x81\x15\x0a\xeb\x84\x5b\xd6\xa8\x74\xfb\x7d\x1d\xcb\x2c\xda" 
    b"\x46\x2a\x76\x62\xce\xbc\x5c\x9e\x8b\xe7\xcf\xbe\x78\xf5\x7c" 
    b"\xeb\xb3\x3a\x9c\xaa\x6f\xcc\x72\xd1\x59\xf2\x11\x23\xd6\x3f" 
    b"\x48\xd1\xb7\xce\xb0\xbf\xcb\xea\x80\xde\x57\xd4\x5e\x97\x2f" 
    b"\x75\xd1\x50\x8e\x80\x2c\x66\x79\xbf\x72\x4b\xbd\x8a\x81\x6c" 
    b"\xd3\xe1\x01\xdc\xd2\x15\x26\xc5\x36\xda\x2c\x1a\xc0\x27\x94" 
    b"\xed\xb7\x9b\x85\x0b\x5e\x80\x97\xc5\xec\x4f\xec\x88\x5d\x50" 
    b"\x07\x35\x47\xdc\x0b\x3b\x3d\xdd\x60\xaf\xa8\x5d\x81\x38\x24" 
    b"\x25\x5d\x5c\x15\xd1\xde\xb3\xab\xec\x05\x69\xef\x83\xed\x57" 
    b"\x54\xb8\x64\x64\x11\x16\x32\x69\xda\x9f\x2d\x7f\x36\xbb\x44" 
    b"\x5a\x34\xe8\x7f\xbf\x03\xeb\x00\x7f\x59\x68\x22\x79\xcf\x73" 
    b"\x6c\x2c\x29\xa7\xa1\x5f\x38\xa1\x1d\xf0\x20\x53\xe0\x1a\x63" 
    b"\x14\x58\x71\x10\xaa\x08\x0c\x3e\x16\x1a\x60\x22\x82\x7f\xba" 
    b"\xa4\x43\xa0\xd0\xac\x1b\xd5\x6b\x64\xb5\x14\x93\x31\x9e\x53" 
    b"\x50\xd0\x57\x66\xee\x5a\x4f\xfb\x03\x2a\x69\x58\x76\xf1\x83" 
    b"\xf7\x4e\xba\x8c\x42\x06\x60\x5d\x6d\xce\x60\x88\xae\xa4\xc3" 
    b"\xf1\x03\xa5\x4b\x98\xa1\xff\x67\xe1\xac\xa2\xb8\x62\xd7\x6f" 
    b"\xa0\x31\xb4\xd2\x77\xaf\x21\x10\x06\xc6\x9a\xff\x1d\x09\x17" 
    b"\x0e\x5f\xf1\xaa\x54\x34\x4b\x45\x8a\x87\x63\xa6\xdc\xf9\x24" 
    b"\x30\x67\xc6\xb2\xd6\x61\x33\x69\xee\x50\x61\x57\x28\xe7\x7e" 
    b"\xee\xec\x3a\x5a\x73\x4e\xa8\x8d\xe4\x18\xea\xec\x41\x64\xc8" 
    b"\xe2\xe8\x66\xb6\x2d\xb6\xfb\x6a\x6c\x16\xb3\xdd\x46\x43\xb9" 
    b"\x73\x00\x6a\x71\xed\x4e\x9d\x25\x1a\xc3\x3c\x4a\x95\x15\x99"
)

_FIRMWARE_DATA_7 = bytearray(
    b"\x35\x81\x14\x02\xd6\x98\x9b\xec\xd8\x23\x3b\x84\x29\xaf\x0c" 
    b"\x99\x83\xa6\x9a\x34\x4f\xfa\xe8\xd0\x3c\x4b\xd0\xfb\xb6\x68" 
    b"\xb8\x9e\x8f\xcd\xf7\x60\x2d\x7a\x22\xe5\x7d\xab\x65\x1b\x95" 
    b"\xa7\xa8\x7f\xb6\x77\x47\x7b\x5f\x8b\x12\x72\xd0\xd4\x91\xef"
    b"\xde\x19\x50\x3c\xa7\x8b\xc4\xa9\xb3\x23\xcb\x76\xe6\x81\xf0" 
    b"\xc1\x04\x8f\xa3\xb8\x54\x5b\x97\xac\x19\xff\x3f\x55\x27\x2f" 
    b"\xe0\x1d\x42\x9b\x57\xfc\x4b\x4e\x0f\xce\x98\xa9\x43\x57\x03" 
    b"\xbd\xe7\xc8\x94\xdf\x6e\x36\x73\x32\xb4\xef\x2e\x85\x7a\x6e" 
    b"\xfc\x6c\x18\x82\x75\x35\x90\x07\xf3\xe4\x9f\x3e\xdc\x68\xf3" 
    b"\xb5\xf3\x19\x80\x92\x06\x99\xa2\xe8\x6f\xff\x2e\x7f\xae\x42" 
    b"\xa4\x5f\xfb\xd4\x0e\x81\x2b\xc3\x04\xff\x2b\xb3\x74\x4e\x36" 
    b"\x5b\x9c\x15\x00\xc6\x47\x2b\xe8\x8b\x3d\xf1\x9c\x03\x9a\x58" 
    b"\x7f\x9b\x9c\xbf\x85\x49\x79\x35\x2e\x56\x7b\x41\x14\x39\x47" 
    b"\x83\x26\xaa\x07\x89\x98\x11\x1b\x86\xe7\x73\x7a\xd8\x7d\x78" 
    b"\x61\x53\xe9\x79\xf5\x36\x8d\x44\x92\x84\xf9\x13\x50\x58\x3b" 
    b"\xa4\x6a\x36\x65\x49\x8e\x3c\x0e\xf1\x6f\xd2\x84\xc4\x7e\x8e" 
    b"\x3f\x39\xae\x7c\x84\xf1\x63\x37\x8e\x3c\xcc\x3e\x44\x81\x45" 
    b"\xf1\x4b\xb9\xed\x6b\x36\x5d\xbb\x20\x60\x1a\x0f\xa3\xaa\x55" 
    b"\x77\x3a\xa9\xae\x37\x4d\xba\xb8\x86\x6b\xbc\x08\x50\xf6\xcc" 
    b"\xa4\xbd\x1d\x40\x72\xa5\x86\xfa\xe2\x10\xae\x3d\x58\x4b\x97" 
    b"\xf3\x43\x74\xa9\x9e\xeb\x21\xb7\x01\xa4\x86\x93\x97\xee\x2f" 
    b"\x4f\x3b\x86\xa1\x41\x6f\x41\x26\x90\x78\x5c\x7f\x30\x38\x4b" 
    b"\x3f\xaa\xec\xed\x5c\x6f\x0e\xad\x43\x87\xfd\x93\x35\xe6\x01"
)

_FIRMWARE_DATA_8 = bytearray(
    b"\xef\x41\x26\x90\x99\x9e\xfb\x19\x5b\xad\xd2\x91\x8a\xe0\x46" 
    b"\xaf\x65\xfa\x4f\x84\xc1\xa1\x2d\xcf\x45\x8b\xd3\x85\x50\x55" 
    b"\x7c\xf9\x67\x88\xd4\x4e\xe9\xd7\x6b\x61\x54\xa1\xa4\xa6\xa2" 
    b"\xc2\xbf\x30\x9c\x40\x9f\x5f\xd7\x69\x2b\x24\x82\x5e\xd9\xd6" 
    b"\xa7\x12\x54\x1a\xf7\x55\x9f\x76\x50\xa9\x95\x84\xe6\x6b\x6d" 
    b"\xb5\x96\x54\xd6\xcd\xb3\xa1\x9b\x46\xa7\x94\x4d\xc4\x94\xb4" 
    b"\x98\xe3\xe1\xe2\x34\xd5\x33\x16\x07\x54\xcd\xb7\x77\x53\xdb" 
    b"\x4f\x4d\x46\x9d\xe9\xd4\x9c\x8a\x36\xb6\xb8\x38\x26\x6c\x0e" 
    b"\xff\x9c\x1b\x43\x8b\x80\xcc\xb9\x3d\xda\xc7\xf1\x8a\xf2\x6d" 
    b"\xb8\xd7\x74\x2f\x7e\x1e\xb7\xd3\x4a\xb4\xac\xfc\x79\x48\x6c" 
    b"\xbc\x96\xb6\x94\x46\x57\x2d\xb0\xa3\xfc\x1e\xb9\x52\x60\x85" 
    b"\x2d\x41\xd0\x43\x01\x1e\x1c\xd5\x7d\xfc\xf3\x96\x0d\xc7\xcb" 
    b"\x2a\x29\x9a\x93\xdd\x88\x2d\x37\x5d\xaa\xfb\x49\x68\xa0\x9c" 
    b"\x50\x86\x7f\x68\x56\x57\xf9\x79\x18\x39\xd4\xe0\x01\x84\x33" 
    b"\x61\xca\xa5\xd2\xd6\xe4\xc9\x8a\x4a\x23\x44\x4e\xbc\xf0\xdc" 
    b"\x24\xa1\xa0\xc4\xe2\x07\x3c\x10\xc4\xb5\x25\x4b\x65\x63\xf4" 
    b"\x80\xe7\xcf\x61\xb1\x71\x82\x21\x87\x2c\xf5\x91\x00\x32\x0c" 
    b"\xec\xa9\xb5\x9a\x74\x85\xe3\x36\x8f\x76\x4f\x9c\x6d\xce\xbc" 
    b"\xad\x0a\x4b\xed\x76\x04\xcb\xc3\xb9\x33\x9e\x01\x93\x96\x69" 
    b"\x7d\xc5\xa2\x45\x79\x9b\x04\x5c\x84\x09\xed\x88\x43\xc7\xab" 
    b"\x93\x14\x26\xa1\x40\xb5\xce\x4e\xbf\x2a\x42\x85\x3e\x2c\x3b" 
    b"\x54\xe8\x12\x1f\x0e\x97\x59\xb2\x27\x89\xfa\xf2\xdf\x8e\x68" 
    b"\x59\xdc\x06\xbc\xb6\x85\x0d\x06\x22\xec\xb1\xcb\xe5\x04\xe6"
)

_FIRMWARE_DATA_9 = bytearray(
    b"\x3d\xb3\xb0\x41\x73\x08\x3f\x3c\x58\x86\x63\xeb\x50\xee\x1d" 
    b"\x2c\x37\x74\xa9\xd3\x18\xa3\x47\x6e\x93\x54\xad\x0a\x5d\xb8" 
    b"\x2a\x55\x5d\x78\xf6\xee\xbe\x8e\x3c\x76\x69\xb9\x40\xc2\x34" 
    b"\xec\x2a\xb9\xed\x7e\x20\xe4\x8d\x00\x38\xc7\xe6\x8f\x44\xa8" 
    b"\x86\xce\xeb\x2a\xe9\x90\xf1\x4c\xdf\x32\xfb\x73\x1b\x6d\x92" 
    b"\x1e\x95\xfe\xb4\xdb\x65\xdf\x4d\x23\x54\x89\x48\xbf\x4a\x2e" 
    b"\x70\xd6\xd7\x62\xb4\x33\x29\xb1\x3a\x33\x4c\x23\x6d\xa6\x76" 
    b"\xa5\x21\x63\x48\xe6\x90\x5d\xed\x90\x95\x0b\x7a\x84\xbe\xb8" 
    b"\x0d\x5e\x63\x0c\x62\x26\x4c\x14\x5a\xb3\xac\x23\xa4\x74\xa7" 
    b"\x6f\x33\x30\x05\x60\x01\x42\xa0\x28\xb7\xee\x19\x38\xf1\x64" 
    b"\x80\x82\x43\xe1\x41\x27\x1f\x1f\x90\x54\x7a\xd5\x23\x2e\xd1" 
    b"\x3d\xcb\x28\xba\x58\x7f\xdc\x7c\x91\x24\xe9\x28\x51\x83\x6e" 
    b"\xc5\x56\x21\x42\xed\xa0\x56\x22\xa1\x40\x80\x6b\xa8\xf7\x94" 
    b"\xca\x13\x6b\x0c\x39\xd9\xfd\xe9\xf3\x6f\xa6\x9e\xfc\x70\x8a" 
    b"\xb3\xbc\x59\x3c\x1e\x1d\x6c\xf9\x7c\xaf\xf9\x88\x71\x95\xeb" 
    b"\x57\x00\xbd\x9f\x8c\x4f\xe1\x24\x83\xc5\x22\xea\xfd\xd3\x0c" 
    b"\xe2\x17\x18\x7c\x6a\x4c\xde\x77\xb4\x53\x9b\x4c\x81\xcd\x23" 
    b"\x60\xaa\x0e\x25\x73\x9c\x02\x79\x32\x30\xdf\x74\xdf\x75\x19"
    b"\xf4\xa5\x14\x5c\xf7\x7a\xa8\xa5\x91\x84\x7c\x60\x03\x06\x3b" 
    b"\xcd\x50\xb6\x27\x9c\xfe\xb1\xdd\xcc\xd3\xb0\x59\x24\xb2\xca" 
    b"\xe2\x1c\x81\x22\x9d\x07\x8f\x8e\xb9\xbe\x4e\xfa\xfc\x39\x65"
    b"\xba\xbf\x9d\x12\x37\x5e\x97\x7e\xf3\x89\xf5\x5d\xf5\xe3\x09" 
    b"\x8c\x62\xb5\x20\x9d\x0c\x53\x8a\x68\x1b\xd2\x8f\x75\x17\x5d"
)

_FIRMWARE_DATA_10 = bytearray(
    b"\xd4\xe5\xda\x75\x62\x19\x14\x6a\x26\x2d\xeb\xf8\xaf\x37\xf0" 
    b"\x6c\xa4\x55\xb1\xbc\xe2\x33\xc0\x9a\xca\xb0\x11\x49\x4f\x68" 
    b"\x9b\x3b\x6b\x3c\xcc\x13\xf6\xc7\x85\x61\x68\x42\xae\xbb\xdd" 
    b"\xcd\x45\x16\x29\x1d\xea\xdb\xc8\x03\x94\x3c\xee\x4f\x82\x11" 
    b"\xc3\xec\x28\xbd\x97\x05\x99\xde\xd7\xbb\x5e\x22\x1f\xd4\xeb" 
    b"\x64\xd9\x92\xd9\x85\xb7\x6a\x05\x6a\xe4\x24\x41\xf1\xcd\xf0" 
    b"\xd8\x3f\xf8\x9e\x0e\xcd\x0b\x7a\x70\x6b\x5a\x75\x0a\x6a\x33" 
    b"\x88\xec\x17\x75\x08\x70\x10\x2f\x24\xcf\xc4\xe9\x42\x00\x61" 
    b"\x94\xca\x1f\x3a\x76\x06\xfa\xd2\x48\x81\xf0\x77\x60\x03\x45" 
    b"\xd9\x61\xf4\xa4\x6f\x3d\xd9\x30\xc3\x04\x6b\x54\x2a\xb7\xec" 
    b"\x3b\xf4\x4b\xf5\x68\x52\x26\xce\xff\x5d\x19\x91\xa0\xa3\xa5" 
    b"\xa9\xb1\xe0\x23\xc4\x0a\x77\x4d\xf9\x51\x20\xa3\xa5\xa9\xb1" 
    b"\xc1\x00\x82\x86\x8e\x7f\x5d\x19\x91\xa0\xa3\xc4\xeb\x54\x0b" 
    b"\x75\x68\x52\x07\x8c\x9a\x97\x8d\x79\x70\x62\x46\xef\x5c\x1b" 
    b"\x95\x89\x71\x41\xe1\x21\xa1\xa1\xa1\xc0\x02\x67\x4c\x1a\xb6" 
    b"\xcf\xfd\x78\x53\x24\xab\xb5\xc9\xf1\x60\x23\xa5\xc8\x12\x87" 
    b"\x6d\x58\x13\x85\x88\x92\x87\x6d\x58\x32\xc7\x0c\x9a\x97\xac" 
    b"\xda\x36\xee\x5e\x3e\xdf\x1d\xb8\xf2\x66\x2f\xbd\xf8\x72\x47" 
    b"\xed\x58\x13\x85\x88\x92\x87\x8c\x7b\x55\x09\x90\xa2\xc6\xef" 
    b"\x3d\xf8\x53\x24\xab\xd4\x2a\xb7\xec\x5a\x36\xee\x5e\x3e\xdf" 
    b"\x3c\xfa\x76\x4f\xfd\x59\x30\xe2\x46\xef\x3d\xf8\x53\x05\x69"
)

_FIRMWARE_DATA_11 = bytearray(
    b"\x31\xc1\x00\x82\x86\x8e\x7f\x5d\x19\xb0\xe2\x27\xcc\xfb\x74" 
    b"\x4b\x14\x8b\x94\x8b\x75\x68\x33\xc5\x08\x92\x87\x8c\x9a\xb6" 
    b"\xcf\x1c\xba\xd7\x0d\x98\xb2\xe6\x2f\xdc\x1b\x95\x89\x71\x60" 
    b"\x23\xc4\x0a\x96\x8f\x9c\xba\xf6\x6e\x3f\xfc\x5b\x15\xa8\xd2" 
    b"\x26\xaf\xbd\xf8\x72\x66\x2f\xdc\x1b\xb4\xcb\x14\x8b\x94\xaa" 
    b"\xb7\xcd\xf9\x51\x01\x80\x82\x86\x6f\x3d\xd9\x30\xe2\x27\xcc" 
    b"\xfb\x74\x4b\x14\xaa\xb7\xcd\xf9\x70\x43\x04\x6b\x35\xc9\xf1" 
    b"\x60\x23\xa5\xc8\xf3\x45\x08\x92\x87\x6d\x58\x32\xe6\x2f\xbd" 
    b"\xf8\x72\x66\x4e\x1e\xbe\xfe\x7e\x7e\x7e\x5f\x1d\x99\x91\xa0" 
    b"\xa3\xc4\x0a\x77\x4d\x18\x93\xa4\xab\xd4\x0b\x75\x49\x10\xa2" 
    b"\xc6\xef\x3d\xf8\x53\x24\xab\xb5\xe8\x33\xe4\x4a\x16\xae\xde" 
    b"\x1f\xbc\xdb\x15\xa8\xb3\xc5\x08\x73\x45\xe9\x31\xc1\xe1\x21" 
    b"\xa1\xa1\xa1\xc0\x02\x86\x6f\x5c\x3a\xd7\x0d\x98\x93\xa4\xca" 
    b"\x16\xae\xde\x1f\x9d\x99\xb0\xe2\x46\xef\x3d\xf8\x72\x47\x0c" 
    b"\x9a\xb6\xcf\xfd\x59\x11\xa0\xa3\xa5\xc8\xf3\x45\x08\x92\x87" 
    b"\x6d\x39\xf0\x43\x04\x8a\x96\xae\xde\x3e\xdf\x1d\x99\x91\xa0" 
    b"\xc2\x06\x6f\x3d\xf8\x72\x47\x0c\x9a\x97\x8d\x98\x93\x85\x88" 
    b"\x73\x45\xe9\x31\xe0\x23\xa5\xa9\xd0\x03\x84\x8a\x96\xae\xde" 
    b"\x1f\xbc\xdb\x15\xa8\xd2\x26\xce\xff\x5d\x19\x91\x81\x80\x82" 
    b"\x67\x2d\xd8\x13\xa4\xab\xd4\x0b\x94\xaa\xb7\xcd\xf9\x51\x20" 
    b"\xa3\xa5\xc8\xf3\x45\xe9\x50\x22\xc6\xef\x5c\x3a\xd7\x0d\x98" 
    b"\x93\x85\x88\x73\x64\x4a\xf7\x4d\xf9\x51\x20\xa3\xc4\x0a\x96"
)

_FIRMWARE_DATA_12 = bytearray(
    b"\xae\xde\x3e\xfe\x7e\x7e\x7e\x5f\x3c\xfa\x76\x4f\xfd\x78\x72" 
    b"\x66\x2f\xbd\xd9\x30\xc3\xe5\x48\x12\x87\x8c\x7b\x55\x28\xd2" 
    b"\x07\x8c\x9a\x97\xac\xda\x17\x8d\x79\x51\x20\xa3\xc4\xeb\x54" 
    b"\x0b\x94\x8b\x94\xaa\xd6\x2e\xbf\xfc\x5b\x15\xa8\xd2\x26\xaf" 
    b"\xdc\x1b\xb4\xea\x37\xec\x3b\xf4\x6a\x37\xcd\x18\x93\x85\x69" 
    b"\x31\xc1\xe1\x40\xe3\x25\xc8\x12\x87\x8c\x9a\xb6\xcf\xfd\x59" 
    b"\x11\xa0\xc2\x06\x8e\x7f\x5d\x38\xf2\x47\x0c\x7b\x74\x6a\x37" 
    b"\xec\x5a\x36\xee\x3f\xfc\x7a\x76\x4f\x1c\x9b\x95\x89\x71\x41" 
    b"\x00\x63\x44\xeb\x54\x2a\xd6\x0f\x9c\xba\xd7\x0d\x98\x93\x85" 
    b"\x69\x31\xc1\x00\x82\x86\x8e\x9e\xbe\xdf\x3c\xfa\x57\x2c\xda" 
    b"\x36\xee\x3f\xfc\x5b\x15\x89\x71\x41\x00\x82\x86\x8e\x7f\x5d" 
    b"\x38\xf2\x47\xed\x58\x13\xa4\xca\xf7\x4d\xf9\x51\x01\x80\x63" 
    b"\x44\xeb\x54\x2a\xd6\x2e\xbf\xdd\x19\x91\xa0\xa3\xa5\xa9\xb1" 
    b"\xe0\x42\x06\x8e\x7f\x5d\x19\x91\xa0\xa3\xc4\x0a\x96\x8f\x7d" 
    b"\x78\x72\x47\x0c\x7b\x74\x6a\x56\x2e\xde\x1f\xbc\xfa\x57\x0d" 
    b"\x79\x51\x01\x61\x21\xa1\xc0\xe3\x25\xa9\xb1\xc1\xe1\x40\x02" 
    b"\x67\x4c\x1a\x97\x8d\x98\x93\xa4\xab\xd4\x2a\xd6\x0f\x9c\x9b" 
    b"\xb4\xcb\x14\xaa\xb7\xcd\xf9\x51\x20\xa3\xc4\xeb\x35\xc9\xf1" 
    b"\x60\x42\x06\x8e\x7f\x7c\x7a\x76\x6e\x3f\xfc\x7a\x76\x6e\x5e" 
    b"\x3e\xfe\x7e\x5f\x3c\xdb\x15\x89\x71\x41\xe1\x21\xc0\xe3\x44" 
    b"\xeb\x54\x2a\xb7\xcd\xf9\x70\x62\x27\xad\xd8\x32\xc7\x0c\x7b" 
    b"\x74\x4b\x14\xaa\xb7\xec\x3b\xd5\x28\xd2\x07\x6d\x39\xd1\x20" 
    b"\xc2\xe7\x4c\x1a\x97\x8d\x98\xb2\xc7\x0c\x59\x28\xf3\x9b"
)

_FIRMWARE_DATA = (
    _FIRMWARE_DATA_1, _FIRMWARE_DATA_2, _FIRMWARE_DATA_3,
    _FIRMWARE_DATA_4, _FIRMWARE_DATA_5, _FIRMWARE_DATA_6,
    _FIRMWARE_DATA_7, _FIRMWARE_DATA_8, _FIRMWARE_DATA_9,
    _FIRMWARE_DATA_10, _FIRMWARE_DATA_11, _FIRMWARE_DATA_12,
)

class PMW3360:
    def __init__(self, sck, mosi, miso, cs):
        self.spi = busio.SPI(sck, mosi, miso)
        self.cs_pin = DigitalInOut(cs)

        self.in_burst = False
        self.last_burst = 0
        
        # SPI Mode 3
        self.device = SPIDevice(self.spi, self.cs_pin, baudrate=8000000, polarity=1, phase=1)
    
    def begin(self, cpi=800):
        self.write_reg(_REG_Shutdown, 0xb6)        # Shutdown first
        self.delay_ms(300)
        self.write_reg(_REG_Power_Up_Reset, 0x5a)  # force reset
        # read registers 0x02 to 0x06 (and discard the data)
        self.read_reg(_REG_Motion)
        self.read_reg(_REG_Delta_X_L)
        self.read_reg(_REG_Delta_X_H)
        self.read_reg(_REG_Delta_Y_L)
        self.read_reg(_REG_Delta_Y_H)
        
        # Upload the firmware
        self.upload_firmware()
        self.delay_ms(10)
        
        # Set default CPI unless specified
        self.set_CPI(cpi)
        
        return self.check_signature()

    # For some reason, the sensor still works as a regular mouse even if the firmware is not uploaded
    def upload_firmware(self):
        # Write 0 to Rest_En bit of Config2 register to disable Rest mode.
        self.write_reg(_REG_Config2, 0x00)
        # write 0x1d in SROM_enable reg for initializing
        self.write_reg(_REG_SROM_Enable, 0x1d)
        # wait for more than one frame period.
        # Assume that the frame rate is as low as 100fps... even if it should never be that low
        self.delay_ms(10)
        # write 0x18 to SROM_enable to start SROM download
        self.write_reg(_REG_SROM_Enable, 0x18)
        
        with self.device as spi:
            spi.write(bytes([_REG_SROM_Load_Burst | 0x80]))
            # send all bytes of the firmware
            for i in range (12):
                for y in range(len(_FIRMWARE_DATA[i])):
                    spi.write(bytes([_FIRMWARE_DATA[i][y]]))
                
        # Read the SROM_ID register to verify the ID before any other register reads or writes.
        self.read_reg(_REG_SROM_ID)
        # Write 0x00 (rest disable) to Config2 register for wired mouse or 0x20 for wireless mouse design. 
        self.write_reg(_REG_Config2, 0x00)

    def constrain(self, val, min_val, max_val):
        return min(max_val, max(min_val, val))

    def set_CPI(self, cpi):
        # limits to 0--119 
        cpival = int(self.constrain((cpi/100)-1, 0, 119))
        
        # Sometimes doesn't work the first time around so keep sending until it does
        while self.get_CPI() != cpi:
            self.write_reg(_REG_Config1, cpival)
              
    # CPI = (cpival + 1)*100
    def get_CPI(self):
        cpival = bytearray(1)
        cpival = self.read_reg(_REG_Config1)

        return (int(cpival[0]) + 1) * 100

    def delay_ms(self, delaytime):
        time.sleep(delaytime / 1000)
        
    def write_reg(self, reg_addr, data):
        if reg_addr != _REG_Motion_Burst:
            self.in_burst = False
        
        with self.device as spi:
        # send adress of the register, with MSBit = 1 to indicate it's a write 
            spi.write(bytes([reg_addr | 0x80]))
            spi.write(bytes([data]))

    def read_reg(self, reg_addr):
        if reg_addr != _REG_Motion_Burst:
            self.in_burst = False

        with self.device as spi:
            # send address of the register, with MSBit = 0 to indicate it's a read
            spi.write(bytes([reg_addr & 0x7f]))
            result = bytearray(1)
            spi.readinto(result)
        
        return result
    
    def check_signature(self):
        pid = self.read_reg(_REG_Product_ID)
        iv_pid = self.read_reg(_REG_Inverse_Product_ID)
        SROM_ver = self.read_reg(_REG_SROM_ID)

        # print("pid", pid[0] == 66)
        # print("iv_pid",  iv_pid[0] == 189)
        # print("SROM_ver", SROM_ver, SROM_ver[0] == 4)
        return (pid[0] == 66 and iv_pid[0] == 189 and SROM_ver[0] == 4)

    def read_burst(self):
        from_last = time.monotonic() - self.last_burst

        if not self.in_burst or from_last > 500:
            self.write_reg(_REG_Motion_Burst, 0x00)
            self.in_burst = True
        
        with self.device as spi:
            spi.write(bytes([_REG_Motion_Burst])) 
            burst_buffer = bytearray(12)
            spi.readinto(burst_buffer) # read burst buffer

        # panic recovery, sometimes burst mode works weird
        if burst_buffer[0] and 0b111: 
            self.in_burst = False

        self.last_burst = time.monotonic()

        motion = (burst_buffer[0] & 0x80) != 0
        surface = (burst_buffer[0] & 0x08) == 0   # 0 if on surface / 1 if off surface

        xl = burst_buffer[2]                      # dx LSB
        xh = burst_buffer[3]                      # dx MSB
        yl = burst_buffer[4]                      # dy LSB
        yh = burst_buffer[5]                      # dy MSB
        sl = burst_buffer[10]                     # shutter LSB
        sh = burst_buffer[11]                     # shutter MSB
        
        x = xh << 8 | xl
        y = yh << 8 | yl
        shutter = sh << 8 | sl

        # public data (change values as needed)
        is_motion = motion                        # True if a motion is detected. 
        is_on_surface = surface                   # True when a chip is on a surface 
        dx = x                                    # displacement on x directions. Unit: Count. (CPI * Count = Inch value)
        dy = y                                    # displacement on y directions.
        SQUAL = burst_buffer[6]                   # Surface Quality register, max 0x80. Number of features on the surface = SQUAL * 8
        raw_data_sum = burst_buffer[7]            # It reports the upper byte of an 18‐bit counter which sums all 1296 raw data in the current frame * Avg value = Raw_Data_Sum * 1024 / 1296
        max_raw_data = burst_buffer[8]            # Max raw data value in current frame, max=127
        min_raw_data = burst_buffer[9]            # Min raw data value in current frame, max=127
        shutter = shutter                         # unit: clock cycles of the internal oscillator. shutter is adjusted to keep the average raw data values within normal operating ranges.

        # create python dictionary and return it
        data = {
            "is_motion" : is_motion,
            "is_on_surface" : is_on_surface,
            "dx" : dx,
            "dy" : dy,
            "SQUAL" : SQUAL,
            "raw_data_sum" : raw_data_sum,
            "max_raw_data" : max_raw_data,
            "min_raw_data" : min_raw_data,
            "shutter" : shutter
        }

        return data

    # May be too slow to be useful when used with read_image_pixel
    def prepare_image(self):
        self.write_reg(_REG_Config2, 0x00)

        self.write_reg(_REG_Frame_Capture, 0x83)
        self.write_reg(_REG_Frame_Capture, 0xc5)

        self.delay_ms(20)
        
        # write burst destination adress
        with self.device as spi:
            spi.write(bytes([_REG_Raw_Data_Burst & 0x7f]))
    
    # May be too slow to be useful
    def read_image_pixel(self):
        with self.device as spi:
            pixel = bytearray(1)
            spi.readinto(pixel)


        return pixel


