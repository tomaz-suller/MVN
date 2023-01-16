from src.mvn_simulator.memory_position import MemoryPosition


def test_valid():
    position = MemoryPosition(0, value=0)
    assert position.value == 0
    assert position.get_value() == 0
    assert position.address == 0
    assert position.get_addr() == 0


def test_default_value():
    position = MemoryPosition(0)
    assert position.value == 0
    assert position.get_value() == 0


def test_valid_init_value():
    position = MemoryPosition(0, value=0xF)
    assert position.value == 0xF
    assert position.get_value() == 0xF


def test_init_overflow():
    position = MemoryPosition(0, value=0x100)
    assert position.value == 0x00


def test_setter_overflow():
    position = MemoryPosition(0)
    position.value = 0x100
    assert position.value == 0x00
