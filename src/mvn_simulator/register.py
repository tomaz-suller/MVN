from .binary import Word


class Register:
    """
    This class is for an register in the MVN, it has only it's
    own value.
    It also has methods to get and set this value
    """
    _value: Word

    def __init__(self, value: int = 0x0000):
        """Initialize the register with value"""
        self.value = value

    @property
    def value(self) -> int:
        return self._value.value

    @value.setter
    def value(self, value: int) -> None:
        self._value = Word(value)

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value
