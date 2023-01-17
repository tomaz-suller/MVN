from .switchcase import switch, case
from .utils import valid_instru, valid_value
from .binary import Word

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

    # pylint: disable=too-many-return-statements
    def execute(self, opcode: int, accumulator_value: int, immediate: int = 0x0000):
        """Check if the given instruction is valid and performs the
        right operation"""

        valid_instru(opcode)
        valid_value(accumulator_value, MIN_VALUE, MAX_VALUE)
        valid_value(immediate, MIN_VALUE, MAX_VALUE)

        switch(opcode)
        if case(1):
            return self.is_zero(accumulator_value)
        if case(2):
            return self.is_negative(accumulator_value)
        if case(4):
            return self.add(accumulator_value, immediate)
        if case(5):
            return self.subtract(accumulator_value, immediate)
        if case(6):
            return self.multiply(accumulator_value, immediate)
        if case(7):
            return self.divide(accumulator_value, immediate)
        if case(0xA):
            return self.not_(accumulator_value)
        if case(0xB):
            return self.and_(accumulator_value, immediate)
        if case(0xC):
            return self.or_(accumulator_value, immediate)
        if case(0xD):
            return self.xor(accumulator_value, immediate)
        return None

    @staticmethod
    def is_zero(operand: int) -> bool:
        return operand == 0x0000

    @staticmethod
    def is_negative(operand: int) -> bool:
        return bool(operand & (1 << 15))

    @staticmethod
    def add(a: int, b: int) -> int:
        return Alu._truncate(a + b)

    @staticmethod
    def subtract(a: int, b: int) -> int:
        return Alu._truncate(a - b)

    @staticmethod
    def multiply(a: int, b: int) -> int:
        return Alu._truncate(a * b)

    @staticmethod
    def divide(a, b):
        sign = +1
        if Alu.is_negative(a):
            a = Alu._opposite(a)
            sign *= -1
        if Alu.is_negative(b):
            b = Alu._opposite(b)
            sign *= -1
        return Alu._truncate(sign * int(a / b))

    @staticmethod
    def not_(a):
        return Alu._truncate(Alu.xor(a, -1))

    @staticmethod
    def and_(a, b):
        return Alu._truncate(a & b)

    @staticmethod
    def or_(a, b):
        return Alu._truncate(a | b)

    @staticmethod
    def xor(a, b):
        return Alu._truncate(a ^ b)

    @staticmethod
    def _truncate(a: int) -> int:
        return Word(a).value

    @staticmethod
    def _opposite(a: int) -> int:
        return Alu._truncate(Alu.not_(a) + 1)
