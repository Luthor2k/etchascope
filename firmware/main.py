from machine import Pin, SPI, SoftSPI, I2C,ADC
import pin_defs
import gc9a01
import gc
import rp2
import sys
from rotary_irq_rp2 import RotaryIRQ
import time
import ustruct
import math

# Constants

# I2C address
ADXL343_ADDR = 0x53

# Registers
REG_DEVID = 0x00
REG_POWER_CTL = 0x2D
REG_DATAX0 = 0x32

# Other constants
DEVID = 0xE5
SENSITIVITY_2G = 1.0 / 256  # (g/LSB)
EARTH_GRAVITY = 9.80665     # Earth's gravity in [m/s^2]
 
def reg_write(i2c, addr, reg, data):
    """
    Write bytes to the specified register.
    """
    
    # Construct message
    msg = bytearray()
    msg.append(data)
    
    # Write out message to register
    i2c.writeto_mem(addr, reg, msg)
    
def reg_read(i2c, addr, reg, nbytes=1):
    """
    Read byte(s) from specified register. If nbytes > 1, read from consecutive
    registers.
    """
    
    # Check to make sure caller is asking for 1 or more bytes
    if nbytes < 1:
        return bytearray()
    
    # Request data from specified register(s) over I2C
    data = i2c.readfrom_mem(addr, reg, nbytes)
    
    return data

class Screen():
    def __init__(self, softSPI=False):
        self.softSPI = softSPI
        self.sck  = Pin(pin_defs.sck, Pin.OUT)
        self.data = Pin(pin_defs.data, Pin.OUT)
        self.dc   = Pin(pin_defs.dc, Pin.OUT)
        self.init()

    def deinit(self):
        self.spi.deinit()
        ## this does not appear to de-initialize the DMAs -- the enable bits are still set
        del(self.spi)
        del(self.tft)
        gc.collect()

    def init(self):
        if self.softSPI:
            self.spi = SoftSPI(baudrate=10_000_000, sck=self.sck, mosi=self.data, miso=Pin(pin_defs.throwaway))
        else:
            self.spi = SPI(0, baudrate=40_000_000, sck=self.sck, mosi=self.data)
        
        self.tft = gc9a01.GC9A01(self.spi, 240, 240,
                            reset     = Pin(pin_defs.reset, Pin.OUT),
                            cs        = Pin(pin_defs.throwaway, Pin.OUT), ## not used, grounded on board
                            dc        = self.dc,
                            backlight = Pin(pin_defs.throwaway, Pin.OUT), ## not used, always on
                            rotation  = 0)
        self.tft.init()   
        self.tft.fill(gc9a01.color565(10,15,10))


if __name__ == "__main__":

    import time
    import random

    ## instantiate and init
    s = Screen()

    ## For everything you can do with the GC9A01 library:
    ## https://github.com/russhughes/gc9a01_mpy

    s.tft.fill(gc9a01.BLACK)

    phosphor_bright = gc9a01.color565(120, 247, 180)
    phosphor_dark   = gc9a01.color565(45, 217, 80)

    # Initialize I2C
    i2c = I2C(1, sda=Pin(14), scl=Pin(15), freq=100000)   

    # Print out any addresses found
    devices = i2c.scan()

    if devices:
        for d in devices:
            print(hex(d))

    #initialize the ADXL345
    # Read device ID to make sure that we can communicate with the ADXL343
    data = reg_read(i2c, ADXL343_ADDR, REG_DEVID)
    if (data != bytearray((DEVID,))):
        print("ERROR: Could not communicate with ADXL343")
        sys.exit()
        
    # Read Power Control register
    data = reg_read(i2c, ADXL343_ADDR, REG_POWER_CTL)
    print(data)

    # Tell ADXL343 to start taking measurements by setting Measure bit to high
    data = int.from_bytes(data, "big") | (1 << 3)
    reg_write(i2c, ADXL343_ADDR, REG_POWER_CTL, data)

    # Test: read Power Control register back to make sure Measure bit was set
    data = reg_read(i2c, ADXL343_ADDR, REG_POWER_CTL)
    print(data)

    #attach rotary interrupt
    r = RotaryIRQ(pin_num_clk=26,
              pin_num_dt=27,
              pull_up=True,
              min_val=0,
              max_val=360,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

    val_old = r.value()
    
    adc = ADC(Pin(28))     # create ADC object on linear pot pin

    while True:
        val_new = r.value()
        slider_adc_value = 65536 - adc.read_u16()  #invert so the linear pot is 'distance from center'

        # Read X, Y, and Z values from registers (16 bits each)
        data = reg_read(i2c, ADXL343_ADDR, REG_DATAX0, 6)

        # Convert 2 bytes (little-endian) into 16-bit integer (signed)
        acc_x = ustruct.unpack_from("<h", data, 0)[0]
        acc_y = ustruct.unpack_from("<h", data, 2)[0]
        acc_z = ustruct.unpack_from("<h", data, 4)[0]

        # Convert measurements to [m/s^2]
        acc_x = acc_x * SENSITIVITY_2G * EARTH_GRAVITY
        acc_y = acc_y * SENSITIVITY_2G * EARTH_GRAVITY
        acc_z = acc_z * SENSITIVITY_2G * EARTH_GRAVITY

        if val_old != val_new:
            val_old = val_new

            rads = 2*math.pi*(float(val_new/360))
            print("rads: ", rads)

            print("slider_adc_value = ", slider_adc_value)
            slider_factor = 120 * slider_adc_value / 65536
            print("slider_factor = ", slider_factor)

            #draw a pixel slider_factor between the center and the edge
            etch_x = int(math.cos(rads) * slider_factor) + 120
            etch_y = int(math.sin(rads) * -1 * slider_factor) + 120
            print("etch_x = ", etch_x, "etch_y = ", etch_y)
            s.tft.pixel(etch_x, etch_y, phosphor_bright)

        if acc_z < -5:
            s.tft.fill(gc9a01.BLACK)
            print("flipped!")

        time.sleep_ms(50)





