import serial
import sys
import time
import numpy as np

# A quick and dirty script to work with an HP Power supply, using the SCPI
# protocol over a serial port.
#
# This script has been tested with an E3644A

class HpSerial(serial.Serial):
    def __init__(self, **kwargs):
        super(HpSerial, self).__init__(**kwargs)
        self.inter_cmd_delay = 0.2     # Seconds
        self.resp_delay = 0.2          # Seconds

    def wr(self, cmd, size=64):
        '''Write and then read'''
        if isinstance(cmd, bytes):
            cmd = cmd.dedode()
        cmd = cmd.rstrip() +'\n'
        if isinstance(cmd, str):
            cmd = cmd.encode()
        print('sending: ' +cmd.decode().strip())
        self.write(cmd)
        if '?' in cmd.decode():
            time.sleep(self.resp_delay)
            resp = self.read_until(size=size).decode().strip()
            print('resp:   ' +resp)
        else:
            resp = ''
        time.sleep(self.inter_cmd_delay)

    def wrtd(self, cmd):
        if isinstance(cmd, str):
            cmd = cmd.encode()
        self.write(cmd)
        time.sleep(self.inter_cmd_delay)

com = '/dev/tty.usbserial-A103LGP6'    # This is how USB-serial dongle shows up on my Mac
if len(sys.argv) > 1:
    com = sys.argv[1]

s = HpSerial(port=com,
        baudrate=9600,  # This appears to be the default for all HP Power Supplies
        bytesize=8,
        parity='N',
        stopbits=2,     # Can't change this. The power supply is hard coded to 2 stob bits
        timeout=2.0,
        xonxoff=0,
        rtscts=0)

s.wr('\n*CLS')
s.wr('SYST:REM')
s.wr('SYST:ERR?')
#s.wr('VOLT 3.0')
#s.wr('VOLT?')
#s.wr('CURR 0.5')
#s.wr('SYST:ERR?')
#s.wr('CURR?')
s.wr('APPL?')
s.wr('SYST:ERR?')

s.wr('OUTP ON')
s.wr('SYST:ERR?')
s.wr('OUTP?')
s.wr('SYST:ERR?')

#VOLTage:RANGe {P8V* | P20V* | P35V** | P60V** | LOW | HIGH}
s.wr('VOLT:RANG P20V')
s.wr('VOLT:RANG?')


for v in np.arange(0, 10, 0.2):
    s.wr('VOLT ' +'{:.3f}'.format(v))
    s.wr('MEAS:CURR?')
    print('')
    time.sleep(0.5)

s.close()
