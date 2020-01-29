# I2C LCD library for LS013B4DN04
# v0.0 beta


import utime
import framebuf
# LCD Control constants
MLCD_WR = 0x01 # MLCD write line command
MLCD_CM =  0x04 # MLCD clear memory command
MLCD_SM  = 0x00 # MLCD static mode command
MLCD_VCOM  = 0x02 # LCD VCOM bit

PIXELS_X = 96						# display is 96x96
PIXELS_Y = 96						# display is 96x96
class LS013B4DN04:

    # Font data. Taken from https://github.com/hsmptg/lcd/blob/master/font.py
    def __init__(self, spi, cs):
        self.buffer = bytearray(96 * 96 // 8)
        self.spi = spi
        self.cs  = cs
        self.fb = framebuf.FrameBuffer(self.buffer, 96, 96, framebuf.MONO_HMSB ) #3=framebuf.MHLSB 'GS2_HMSB', 'GS4_HMSB', 'GS8', 'MONO_HLSB', 'MONO_HMSB', 'MONO_VLSB', 'MVLSB', 'RGB565'
        self.reset()

    def reset(self):
        self.cs.value(1)
        utime.sleep_us(6) # tsSCS
        self.spi.write(bytes([MLCD_CM, 0x00, 0x00])) # send clear + DUMMY DATA
        utime.sleep_us(2) # thSCS
        self.cs.value(0)
        self.fb.fill(0)

    def _data(self):
        '''
        #MVLSB to MHLSB
        bufr = bytearray(96 * 96 // 8)
        for y in range(0,12):
            for x in range(0,12):
                for i in range(0,8): #X
                    for j in range(0,8): #
                        if self.buffer[(y*8 )*12 + x*8 + j ] & 2**(7-i) == 0:
                            bufr[((11-y)*8 + i )*12 + (11-x) ] = bufr[((11-y)*8 + i )*12 + (11-x) ] | 2**(7-j)

        '''



        bufr = self.buffer
        """
        # rotate 90°
        bufr = bytearray(96 * 96 // 8)
        fbV = framebuf.FrameBuffer(bufr, 96, 96, framebuf.MONO_HMSB )
        for y in range(0,96):
            for x in range(0,96):
                fbV.pixel(x,y,self.fb.pixel(y,95-x))
        """
        #write
        for line in range (1,PIXELS_Y):
            dataLine=bytearray()
            for column in range (0,(PIXELS_X/8)):
                dataLine.append(bufr[(line-1)*int((PIXELS_X/8))+column ])
            utime.sleep_us(2) # twSCSL
            self.cs.value(1)
            utime.sleep_us(6) # tsSCS
            dataLineF=bytes([MLCD_WR, line]) + dataLine + bytes([0x00, 0x00])
            #dataLineF=bytes([MLCD_WR, line ,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00,0x00])
            self.spi.write(dataLineF) #line + DUMMY DATA
            #print("send : {}".format(dataLineF))
            utime.sleep_us(2) # thSCS
            self.cs.value(0)

    def text(self, char, x, y):
        self.fb.fill_rect(x,y,96,8,0) #clear old text
        self.fb.text(char,x,y,1)
        self._data()

    def fill(self,c):
        self.fb.fill(c)

    def fill_rect(self,x, y, w, h, c):
        self.fb.fill_rect(x, y, w, h, c)
        self._data()

    def hline(self,x, y, w, c):
        self.fb.hline(x, y, w, c)
        self._data()

    def vline(self,x, y, h, c):
         self.fb.vline(x, y, h, c)


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
