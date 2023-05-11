import PMW3360
import board, time
from digitalio import DigitalInOut, Direction
import usb_hid
from adafruit_hid.mouse import Mouse

mouse = Mouse(usb_hid.devices)

sensor = PMW3360.PMW3360(board.CLK, board.MOSI, board.MISO, board.D10)

mt_pin = DigitalInOut(board.A0)
mt_pin.direction = Direction.INPUT

sensor.begin()

def constrain(val, min_val, max_val):
    return min(max_val, max(min_val, val))

# Normalizes value into a signed value
def delta(value):
    # Negative if MSB is 1
    if value & 0x8000:
        return -(~value & 0x7fff)
    else:
        return value & 0x7fff

while True:
    data = sensor.read_burst()
    dx = delta(data["dx"])
    dy = delta(data["dy"])
    
    # Limit values if needed
    # dx = constrain(delta(data["dx"]), -127, 127
    # dy = constrain(delta(data["dy"]), -127, 127)

    # uncomment if mt_pin isn't used 
    # if data["isOnSurface"] == True and data["isMotion"] and mt_pin.value == True:
    if mt_pin.value == 0:
        print(dx)
        print(dy)
        print("")

        mouse.move(dx, dy)





