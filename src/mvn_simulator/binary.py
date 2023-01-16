from dataclasses import dataclass, field


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
        return (
            (self.most_significant.value << 4)
            + self.least_significant.value
        )
