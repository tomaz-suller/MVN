from dataclasses import dataclass


@dataclass
class Nibble:
    value: int = 0

    def __post_init__(self):
        if not 0x0 <= self.value <= 0xF:
            raise ValueError(f"value {self.value} does not fit into a nibble")


@dataclass
class Byte:
    value: int = 0

    def __post_init__(self):
        if not 0x00 <= self.value <= 0xFF:
            raise ValueError(f"value {self.value} does not fit into a byte")
