from dataclasses import dataclass, field


# TODO Remove Nibble and store value directly on Byte
@dataclass
class Nibble:
    value: int = 0x0

    def __post_init__(self):
        self.value = self.value & 0xF


@dataclass
class Byte:
    most_significant: Nibble = field(init=False, compare=False)
    least_significant: Nibble = field(init=False, compare=False)

    def __init__(self, value: int = 0x00):
        self.most_significant = Nibble((value & 0xF0) >> 4)
        self.least_significant = Nibble(value & 0x0F)

    @property
    def value(self) -> int:
        return (self.most_significant.value << 4) + self.least_significant.value


@dataclass
class Word:
    most_significant: Byte = field(init=False, compare=False)
    least_significant: Byte = field(init=False, compare=False)

    def __init__(self, value: int = 0x0000):
        self.most_significant = Byte((value & 0xFF00) >> 8)
        self.least_significant = Byte(value & 0x00FF)

    @property
    def value(self) -> int:
        return (self.most_significant.value << 8) + self.least_significant.value

    def as_ascii(self) -> str:
        return chr(self.most_significant.value) + chr(self.least_significant.value)
