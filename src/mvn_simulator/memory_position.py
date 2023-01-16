from .binary import Byte


class MemoryPosition:
    """
    This class is for an address in the memory, it is defined by
    one address number and one value contained in this address.
    It also contains to get address and value and to set the value
    """

    def __init__(self, address: int, value: int = 0x00):
        """Inicialize address and value"""
        self._address: int = None
        self._content: Byte = None
        self.address = address
        self.value = value

    @property
    def address(self) -> int:
        return self._address

    @address.setter
    def address(self, address: int):
        self._address = address

    @property
    def value(self) -> int:
        return self._content.value

    @value.setter
    def value(self, value: int):
        self._content = Byte(value)

    def set_value(self, value: int):
        self.value = value

    def get_addr(self) -> int:
        return self.address

    def get_value(self) -> int:
        return self.value
