from .switchcase import *
from .utils import *

MIN_VALUE = 0x0000
MAX_VALUE = 0xFFFF


class Alu:
    """
    This class represents a simple Arithmetic Logic Unit
    (ALU)

    This ALU can only
    operate equal zero, less than zero, addition, subtraction,
    multiplication and division mapped in the operations 1,2,4,5,6,7
    respectively.
    It contains methods for all of these operations and one method
    to call the others.
    """

    def __init__(self):
        """Inicialize the LAU"""

    def execute(self, op, ac, oi=0x0000):
        """Check if the given instruction is valid and performs the
        right operation"""

        valid_instru(op)
        valid_value(ac, MIN_VALUE, MAX_VALUE)
        valid_value(oi, MIN_VALUE, MAX_VALUE)
        switch(op)
        if case(1):
            return self.is_zero(ac)
        if case(2):
            return self.is_neg(ac)
        if case(4):
            return self.add(ac, oi)
        if case(5):
            return self.sub(ac, oi)
        if case(6):
            return self.mul(ac, oi)
        if case(7):
            return self.div(ac, oi)
        if case(0xA):
            return self._not(ac)
        if case(0xB):
            return self._and(ac, oi)
        if case(0xC):
            return self._or(ac, oi)
        if case(0xD):
            return self._xor(ac, oi)

    def is_zero(self, num):
        return num == 0x0000

    def is_neg(self, num):
        return num >= 0x8000

    def add(self, num1, num2):
        return (num1 + num2) % (1 << 16)

    def sub(self, num1, num2):
        return (num1 - num2) % (1 << 16)

    def mul(self, num1, num2):
        return (num1 * num2) % (1 << 16)

    def div(self, num1, num2):
        signal = False
        if self.is_neg(num1):
            num1 = self.mul(num1, 0xFFFF)
            signal = not signal
        if self.is_neg(num2):
            num2 = self.mul(num2, 0xFFFF)
            signal = not signal
        if signal:
            return self.mul(num1 // num2, 0xFFFF)
        return num1 // num2

    def _not(self, num):
        return num ^ 0xFFFF

    def _and(self, num1, num2):
        return num1 & num2

    def _or(self, num1, num2):
        return num1 | num2

    def _xor(self, num1, num2):
        return num1 ^ num2
