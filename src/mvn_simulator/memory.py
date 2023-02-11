import io
from collections import UserDict
from pathlib import Path

from .binary import Byte, Word
from .utils import MvnError, hex_zfill


class Memory(UserDict[int, Byte]):
    """
    This class represents the memory of the MVN, it has an
    collection of addresses that vary from 0x0000 to 0xFFFF.
    It contains methods to get, set and print those values.
    """

    LAST_MEMORY_ADDRESS: int = 0xFFF  # Addresses vary from 0x0..=0xFFF

    def _check_address(self, address: int) -> None:
        if 0x000 <= address <= self.LAST_MEMORY_ADDRESS:
            return
        raise MvnError(
            f"address {self._format_address(address)} cannot be accessed; "
            f"addresses vary from 0 to {self.LAST_MEMORY_ADDRESS}"
        )

    def __getitem__(self, key: int) -> Byte:
        self._check_address(key)
        return self.data.get(key, Byte(0))

    def __setitem__(self, key: int, item: Byte) -> None:
        self._check_address(key)
        return super().__setitem__(key, item)

    def get_value(self, address: int) -> int:
        try:
            self._check_address(address)
            self._check_address(address + 1)
        except MvnError as error:
            raise MvnError(
                f"aligned access to address {self._format_address(address)} failed"
            ) from error
        return (self[address].value << 8) + self[address + 1].value

    def set_value(self, address: int, value: int) -> None:
        value_word = Word(value)
        try:
            self._check_address(address)
            self._check_address(address + 1)
            self[address] = value_word.most_significant
            self[address + 1] = value_word.least_significant
        except MvnError as error:
            raise MvnError(
                f"aligned assignment to address {self._format_address(address)} failed"
            ) from error

    def show(self, first_address: int, last_address: int, filepath: Path = None):
        self._check_address(first_address)
        self._check_address(last_address)
        if first_address > last_address:
            raise MvnError("Incompatible values")

        with io.StringIO() as buffer:
            buffer.write(
                "       "
                + "  ".join((hex_zfill(i, 2) for i in range(0x10)))
                + "\n"
                + "-" * 71
            )
            # FIXME Refactor to iterate over lines and join line values
            for address in range(first_address, last_address + 1):
                if not address & 0xF:
                    # Last address nibble is in the columns
                    address_but_last_nibble = address & 0xFFF0
                    buffer.write(
                        "\n" + hex_zfill(address_but_last_nibble & 0xFFF0, 4) + ":  "
                    )
                buffer.write(hex_zfill(self[address].value, 2) + " " * 2)
            text = buffer.getvalue()

        if filepath is not None:
            with open(filepath, "w", encoding="utf8") as file:
                file.write(text)
        else:
            print(text)

    @staticmethod
    def _format_address(address: int) -> str:
        return f"0x{address:04X}"
