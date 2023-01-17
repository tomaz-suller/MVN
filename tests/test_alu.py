from mvn_simulator.alu import Alu


class TestIsZero:
    def test_zero(self):
        assert Alu.is_zero(0)

    def test_positive(self):
        assert not Alu.is_zero(1)

    def test_negative(self):
        assert not Alu.is_zero(-1)


class TestIsNegative:
    def test_negative_integer(self):
        assert Alu.is_negative(-1)
        assert Alu.is_negative(-32767)
        assert Alu.is_negative(-32768)

    def test_negative_integer_beyond_two_bytes(self):
        assert not Alu.is_negative(-32769)
        assert not Alu.is_negative(-100000)

    def test_positive_integer(self):
        assert not Alu.is_negative(0x0FFF)
        assert not Alu.is_negative(0x10000)

    def test_positive_integer_negative_in_two_complement(self):
        assert Alu.is_negative(1 << 15)
        assert Alu.is_negative(0xFFFF)


def test_add():
    assert Alu.add(1, 2) == 3
    assert Alu.add(1, -2) == 0xFFFF
    assert Alu.add(-1, 2) == 1
    assert Alu.add(-1, -2) == 0xFFFD
    assert Alu.add(0xFFFE, 0x0001) == 0xFFFF
    assert Alu.add(0xFFFF, 0x0001) == 0x0000


def test_subtract():
    assert Alu.subtract(1, 2) == 0xFFFF
    assert Alu.subtract(1, -2) == 3
    assert Alu.subtract(-1, 2) == 0xFFFD
    assert Alu.subtract(-1, -2) == 1


def test_multiply():
    assert Alu.multiply(1, 0) == 0

    assert Alu.multiply(1, 2) == 2
    assert Alu.multiply(-1, 2) == 0xFFFE
    assert Alu.multiply(1, -2) == 0xFFFE
    assert Alu.multiply(-1, -2) == 2

    assert Alu.multiply(2, 2) == 4

    assert Alu.multiply(0xFFFF, 0x0010) == 0xFFF0


def test_divide():
    assert Alu.divide(1, 2) == 0

    assert Alu.divide(5, 2) == 2
    assert Alu.divide(5, -2) == 0xFFFE
    assert Alu.divide(-5, 2) == 0xFFFE
    assert Alu.divide(-5, -2) == 2


def test_not():
    assert Alu.not_(0x0000) == 0xFFFF
    assert Alu.not_(0x000F) == 0xFFF0
    assert Alu.not_(0xF0FF) == 0x0F00


def test_and():
    assert Alu.and_(0xF0F0, 0xFF00) == 0xF000


def test_or():
    assert Alu.or_(0xF0F0, 0xFF00) == 0xFFF0


def test_xor():
    assert Alu.xor(0xF0F0, 0xFF00) == 0x0FF0
