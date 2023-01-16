import select
import subprocess
import sys

from .utils import *
from .switchcase import *

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF


class Device:
    """
    This class represents an simple I/O device for MVN, it can
    hold monitor (output), keyboard (input), printer (output)
    or file (input and/or output).
    It contains methods to return weather the device is readable
    or writable, to input and output data, to get device type and
    UC, to print the possible devices and to terminate it.
    """

    def __init__(self, dtype, UC, file=None, rwb=None, printer=None, quiet=False):
        """Inicialize the device given the type, the UC and other
        convinient parameters"""

        valid_type(dtype)
        self.dtype = dtype
        self.UC = UC
        self.quiet = quiet
        self.rwb = rwb

        if self.dtype == 3:
            valid_rwb(rwb)
            switch(rwb)
            if case("e"):
                self.file_write = open(file, "wb")
                self.file_read = None
            elif case("l"):
                valid_file(file)
                self.file_write = None
                self.file_read = open(file, "rb")
                self.buffer = self.file_read.read()
                self.counter = 0
                self.file = file
        elif self.dtype == 2:
            valid_printer(printer)
            self.printer = printer
        elif self.dtype == 0:
            self.buffer = []

    def is_readable(self):
        """Return True weather the device is readable"""
        return self.dtype == 0 or (self.dtype == 3 and self.file_read is not None)

    def is_writable(self):
        """Return True weather the device is writable"""
        return (
            self.dtype == 1
            or self.dtype == 2
            or self.dtype == 3
            and self.file_write is not None
        )

    def has_buffer(self):
        """Return True weather the device has buffer"""
        return self.dtype == 0 or (self.dtype == 3 and self.rwb != "e")

    def get_data(self, limit):
        """Get data from the device and return it, the limit to be
        returned is one byte (or two nibbles)"""

        if not self.is_readable():
            raise MvnError("Unreadable device")
        switch(self.dtype)
        if case(0):
            if len(self.buffer) < 2:
                if limit == None:
                    read = input()
                    for nibble in read:
                        self.buffer.append(ord(nibble))
                    self.buffer.append(ord("\n"))
                else:
                    read, o, e = select.select([sys.stdin], [], [], limit / 1000)
                    if read:
                        for nibble in sys.stdin.readline().strip():
                            self.buffer.append(ord(nibble))
                    else:
                        if self.quiet:
                            print("Not enough data on buffer, returning 0x0000")
                        return 0x0000
                    self.buffer.append(ord("\n"))
            if len(self.buffer) > 1:
                return self.buffer.pop(0) * 0x0100 + self.buffer.pop(0)
            else:
                if self.quiet:
                    print("Not enough data on buffer, returning 0x0000")
                return 0x0000
        elif case(3):
            if self.counter + 2 > len(self.buffer):
                if self.quiet:
                    print("No more data to get, returning 0x0000")
                return 0x0000
            else:
                self.counter += 2
                return (
                    self.buffer[self.counter - 2] * 0x0100
                    + self.buffer[self.counter - 1]
                )

    def put_data(self, value):
        """Put given data to the device, the limit to be put is one
        byte (or two nibbles)"""

        if not self.is_writable():
            raise MvnError("Unwritable device")
        valid_value(value, MIN_VALUE, MAX_VALUE)
        switch(self.dtype)
        if case(1):
            print(chr(value // 0x0100) + chr(value % 0x0100))
        elif case(2):
            out = open("will_print.txt", "rb")
            out.write(value // 0x0100)
            out.write(value % 0x0100)
            subprocess.run("lpr -P " + self.printer + " will_print.txt")
            subprocess.run("rm will_print.txt")
        elif case(3):
            self.file_write.write((value // 0x0100).to_bytes(1, byteorder="big"))
            self.file_write.write((value % 0x0100).to_bytes(1, byteorder="big"))
            self.file_write.flush()

    def append_buffer(self):
        if not self.is_readable() or self.dtype != 3:
            raise MvnError("Unreadable device")
        self.file_read.close()
        self.file_read = open(self.file, "rb")
        self.buffer = self.file_read.read()

    def clean_buffer(self):
        if not self.has_buffer():
            raise MvnError("No buffer to be cleaned")
        switch(self.dtype)
        if case(0):
            self.buffer = []
        elif case(3):
            self.buffer = ""
            self.counter = 0

    def terminate(self):
        """Ends up the device"""
        if self.dtype == 3:
            try:
                self.file_write.close()
            except:
                pass

            try:
                self.file_read.close()
            except:
                pass

    def get_type(self):
        """Return device type"""
        return self.dtype

    def get_UC(self):
        """Return device UC"""
        return self.UC

    def show_available(self):
        """Print the possible devices"""
        print("Tipos de dispositivos disponíveis:")
        print("   Teclado    -> 0")
        print("   Monitor    -> 1")
        print("   Impressora -> 2")
        print("   Disco      -> 3")


# Easter eggs taken from https://www.oocities.org/spunk1111/easter.htm
