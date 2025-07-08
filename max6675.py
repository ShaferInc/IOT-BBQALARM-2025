# MAX6675 MicroPython Driver
from machine import Pin
import time

class MAX6675:
    def __init__(self, sck, cs, so):
        self.sck = sck
        self.cs = cs
        self.so = so
        self.cs.value(1)

    def read(self):
        self.cs.value(0)
        time.sleep_us(10)
        
        value = 0
        for i in range(16):
            self.sck.value(1)
            time.sleep_us(1)
            if self.so.value():
                value = (value << 1) | 1
            else:
                value = value << 1
            self.sck.value(0)
            time.sleep_us(1)
            
        self.cs.value(1)

        if (value & 0x4):
            raise Exception("Thermocouple is not connected.")

        temp_data = (value >> 3) & 0xFFF
        celsius = temp_data * 0.25
        
        return celsius