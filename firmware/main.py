from machine import Pin, SPI, SoftSPI, I2C
import pin_defs
import gc9a01
import gc
import rp2
import sys
from rotary_irq_rp2 import RotaryIRQ
import time
import math

# Constants
ADXL345_ADDRESS = 0x53
ADXL345_POWER_CTL = 0x2D
ADXL345_DATA_FORMAT = 0x31
ADXL345_DATAX0 = 0x32
 
# Initialize ADXL345
def init_adxl345():
    i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_POWER_CTL, bytearray([0x08]))  # Set bit 3 to 1 to enable measurement mode
    i2c.writeto_mem(ADXL345_ADDRESS, ADXL345_DATA_FORMAT, bytearray([0x0B]))  # Set data format to full resolution, +/- 16g
 
# Read acceleration data
def read_accel_data():
    data = i2c.readfrom_mem(ADXL345_ADDRESS, ADXL345_DATAX0, 6)
    x, y, z = ustruct.unpack('<3h', data)
    return x, y, z



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

    #s.tft.fill(gc9a01.BLUE)
    #time.sleep_ms(1000)
    #s.tft.fill(gc9a01.YELLOW)
    #time.sleep_ms(1000)
    s.tft.fill(gc9a01.BLACK)

    phosphor_bright = gc9a01.color565(120, 247, 180)
    phosphor_dark   = gc9a01.color565(45, 217, 80)

    '''

    ## better graphic demo should go here
    for i in range(2):
        x1 = random.randint(0, 240)
        x2 = random.randint(0, 240)
        y1 = random.randint(0, 240)
        y2 = random.randint(0, 240)

        if i % 2:
            s.tft.line(x1, y1, x2, y2, phosphor_bright)
        else:
            s.tft.line(x1, y1, x2, y2, phosphor_dark)
        time.sleep_ms(20)
    '''

    # Initialize I2C
    i2c = I2C(1, sda=Pin(pin_defs.i2c_exp_sda), scl=Pin(pin_defs.i2c_exp_scl), freq=400000)   
    # Print out any addresses found
    devices = i2c.scan()

    if devices:
        for d in devices:
            print(hex(d))
    
    r = RotaryIRQ(pin_num_clk=26,
              pin_num_dt=27,
              pull_up=True,
              min_val=0,
              max_val=360,
              reverse=False,
              range_mode=RotaryIRQ.RANGE_WRAP)

    val_old = r.value()

    while True:
        val_new = r.value()

        if val_old != val_new:
            val_old = val_new
            rads = 2*math.pi*(float(val_new/360))
            arc_x = math.cos(rads) * 120 + 120
            arc_y = math.sin(rads) * -120 + 120
            print('result =', val_new, "arc_x = ", arc_x, "arc_y = ", arc_y)
            #s.tft.line(120, 120, int(arc_x), int(arc_y), phosphor_bright)
            s.tft.pixel(int(arc_x), int(arc_y), phosphor_bright)

        time.sleep_ms(20)





