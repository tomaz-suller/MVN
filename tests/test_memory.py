import pytest

from mvn_simulator.binary import Word
from mvn_simulator.memory import Memory
from mvn_simulator.utils import MvnError


# _ is necessary so pytest doesn't detect this as a test class
class _TestAccess:
    memory: Memory
    memory_content: dict[int, int]
    invalid_address: int

    def test_initial_value_is_zero(self):
        for address in self.memory_content.keys():
            assert self.memory.get_value(address) == 0

    def test_get_value_on_valid_address(self):
        # We exploit the internal, ideally private API to
        # test read without testing write
        for key, value in self.memory_content.items():
            word = Word(value)
            self.memory.data[key] = word.most_significant
            self.memory.data[key + 1] = word.least_significant

        for address, value in self.memory_content.items():
            assert self.memory.get_value(address) == value

    def test_set_value_on_valid_address(self):
        for address, value in self.memory_content.items():
            self.memory.set_value(address, value)
            assert self.memory.get_value(address) == value

    def test_get_value_on_invalid_address(self):
        with pytest.raises(MvnError, match=r"access to address 0x[\dA-F]{4} failed"):
            self.memory.get_value(self.invalid_address)

    def test_set_value_on_invalid_address(self):
        with pytest.raises(MvnError, match=r"to address 0x[\dA-F]{4} failed"):
            self.memory.set_value(self.invalid_address, 0x1101)

    def test_overflow(self):
        address, _ = self.memory_content.popitem()
        for overflow_value in (0x10000, 0x20000, 0xF0000):
            self.memory.set_value(address, overflow_value)
            assert self.memory.get_value(address) == 0


class TestAlignedAccess(_TestAccess):
    memory = Memory()
    memory_content = {
        0x000: 0x1010,
        0x00E: 0x0101,
        0x010: 0x1100,
        0xFFE: 0x0011,
    }
    invalid_address = 0x1000


class TestUnalignedAccess(_TestAccess):
    memory = Memory()
    memory_content = {
        0x001: 0x1010,
        0x00F: 0x0101,
        0x011: 0x1100,
        0xFFD: 0x0011,
    }
    invalid_address = 0x1001
