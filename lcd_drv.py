# MicroPython SSD1306 OLED driver, I2C and SPI interfaces
import framebuf
import utime

# register definitions
MLCD_WR = const(0x01) # MLCD write line command
MLCD_CM =  const(0x04) # MLCD clear memory command
MLCD_SM  = const(0x00) # MLCD static mode command
MLCD_VCOM  = const(0x02) # LCD VCOM bit

PIXELS_X = 96						# display is 96x96
PIXELS_Y = 96						# display is 96x96
# Subclassing FrameBuffer provides support for graphics primitives
# http://docs.micropython.org/en/latest/pyboard/library/framebuf.html
class LS013B4DN04(framebuf.FrameBuffer):
    def __init__(self, spi, cs):
        self.spi = spi
        self.cs  = cs
        self.buffer = bytearray(96 * 96 // 8)
        super().__init__(self.buffer, PIXELS_X, PIXELS_X, framebuf.MONO_HMSB)
        self.init_display()

    def init_display(self):
        for cmd in (
            MLCD_CM, #  MLCD clear memory command
			):
            self.write_cmd(cmd)
        self.fill(0)
        self.show()

    def invert(self, invert):
        #self.write_cmd(SET_NORM_INV | (invert & 1))
		pass

    def show(self):
        self.write_data(self.buffer)

    def write_cmd(self, cmd):
        self.cs.value(1)
        self.spi.write(bytes([cmd, 0x00, 0x00]))
        self.cs.value(0)

    def write_data(self, buf):
		for line in range (1,PIXELS_Y):
			dataLine=bytearray()
			for column in range (0,(PIXELS_X/8)):
				dataLine.append(buf[(line-1)*int((PIXELS_X/8))+column ])
			utime.sleep_us(2) # twSCSL
			self.cs.value(1)
			utime.sleep_us(6) # tsSCS
			dataLineF=bytes([MLCD_WR, line]) + dataLine + bytes([0x00, 0x00])
			#dataLineF=bytes([MLCD_WR, line ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
			self.spi.write(dataLineF) #line + DUMMY DATA
			#print("send : {}".format(dataLineF))
			utime.sleep_us(2) # thSCS
			self.cs.value(0)

if __name__ == "__main__":
    import sys,  machine,  os
    from machine import SPI
    from machine import Pin
    print("Started")
    #Display
    spi = SPI(0, mode=SPI.MASTER, baudrate=1000000, polarity=0, phase=0, firstbit=SPI.LSB)
    cs  = Pin('P9', mode=Pin.OUT)
    display = LS013B4DN04(spi, cs=cs)
    display.text("hello word",10,10)
    display.text("hello word",10,20)
    display.hline(0,10,96, 1)
    display.show()
    with open('icon/bluetooth.pbm', 'rb') as f:
        f.readline() # Magic number
        while True:
            l = f.readline()
            if l[0] != "#" :break
        f.readline() # Dimensions
        data = bytearray(f.read())
    print(len(data))
    fbuf = framebuf.FrameBuffer(data, 16, 16, framebuf.MONO_HMSB)
    display.blit(fbuf, 0, 0)
    display.show()
