from src.mvn_simulator.binary import Nibble, Byte, Word


def test_valid_nibble():
    for value in range(0, 0x10):
        nibble = Nibble(value)
        assert nibble.value == value


def test_default_nibble():
    nibble = Nibble()
    assert nibble.value == 0


def test_nibble_overflow():
    nibble = Nibble(0x10)
    assert nibble.value == 0
    nibble = Nibble(0x11)
    assert nibble.value == 1
    nibble = Nibble(0x1F)
    assert nibble.value == 0xF


def test_valid_byte():
    for value in range(0, 0x100):
        print(value)
        byte = Byte(value)
        assert byte.value == value


def test_default_byte():
    byte = Byte()
    assert byte.value == 0


def test_byte_overflow():
    byte = Byte(0x100)
    assert byte.value == 0x00
    byte = Byte(0x101)
    assert byte.value == 0x01
    byte = Byte(0x111)
    assert byte.value == 0x11
    byte = Byte(0xFFF)
    assert byte.value == 0xFF


def test_valid_word():
    for value in range(0, 0x10000):
        print(value)
        word = Word(value)
        assert word.value == value


def test_default_word():
    word = Word()
    assert word.value == 0


def test_word_overflow():
    word = Word(0x10000)
    assert word.value == 0x0000
    word = Word(0x10001)
    assert word.value == 0x0001
    word = Word(0x11111)
    assert word.value == 0x1111
    word = Word(0xFFFFF)
    assert word.value == 0xFFFF
