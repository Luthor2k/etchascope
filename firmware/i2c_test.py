import machine

# Create I2C object
i2c = machine.I2C(1, scl=machine.Pin(15), sda=machine.Pin(14))

# Print out any addresses found
devices = i2c.scan()

if devices:
    for d in devices:
        print(hex(d))