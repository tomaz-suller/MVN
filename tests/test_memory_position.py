import pytest

from mvn_simulator.memory_position import MemoryPosition
from src.mvn_simulator.utils import MvnError


def test_valid():
    address = MemoryPosition(0, value=0)
    assert address.value == 0
    assert address.get_value() == 0
    assert address.address == 0
    assert address.get_addr() == 0


def test_default_value():
    address = MemoryPosition(0)
    assert address.value == 0
    assert address.get_value() == 0


def test_valid_init_value():
    address = MemoryPosition(0, value=0xF)
    assert address.value == 0xF
    assert address.get_value() == 0xF


def test_invalid_init_value_larger_than_ff():
    with pytest.raises(MvnError, match="does not fit"):
        MemoryPosition(0, value=0x100)


def test_invalid_setter_value_larger_than_ff():
    address = MemoryPosition(0)
    with pytest.raises(MvnError, match="does not fit"):
        address.value = 0x100


def test_invalid_set_value_larger_than_ff():
    address = MemoryPosition(0)
    with pytest.raises(MvnError, match="does not fit"):
        address.set_value(0x100)


def test_invalid_init_value_smaller_than_0():
    with pytest.raises(MvnError, match="does not fit"):
        MemoryPosition(0, value=-1)


def test_invalid_setter_value_smaller_than_0():
    address = MemoryPosition(0)
    with pytest.raises(MvnError, match="does not fit"):
        address.value = -1


def test_invalid_set_value_smaller_than_0():
    address = MemoryPosition(0)
    with pytest.raises(MvnError, match="does not fit"):
        address.set_value(-1)
