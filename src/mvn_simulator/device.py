import signal
from dataclasses import dataclass
from enum import Enum, IntEnum
from pathlib import Path

from .binary import Word
from .utils import MvnError


class DeviceType(IntEnum):
    KEYBOARD = 0
    DISPLAY = 1
    PRINTER = 2  # Deprecated, does nothing and should not be used
    DISK = 3


class DeviceMode(str, Enum):
    NONE = ""
    READ = "l"
    WRITE = "e"

    # TODO Consider using or removing
    @property
    def open_mode(self) -> str:
        if self == DeviceMode.READ:
            return "r"
        if self == DeviceMode.WRITE:
            return "wb"
        raise ValueError("device mode doesn't allow opening files")


@dataclass
class DeviceConfig:
    type: DeviceType
    identifier: int
    mode: DeviceMode = DeviceMode.NONE

    # TODO Implement
    # @staticmethod
    # def parse(config: str) -> "DeviceConfig":
    #     ...

    @property
    def is_readable(self):
        return self.type == DeviceType.KEYBOARD or (
            self.type == DeviceType.DISK and self.mode == DeviceMode.READ
        )

    @property
    def is_writable(self):
        return (
            self.type == DeviceType.DISPLAY
            or self.type == DeviceType.PRINTER
            or (self.type == DeviceType.DISK and self.mode == DeviceMode.WRITE)
        )

    @property
    def has_buffer(self):
        return self.type == DeviceType.KEYBOARD or (
            self.type == DeviceType.DISK and self.mode == DeviceMode.READ
        )


class Device:
    """
    This class represents an simple I/O device for MVN, it can
    hold monitor (output), keyboard (input), printer (output)
    or file (input and/or output).
    It contains methods to return weather the device is readable
    or writable, to input and output data, to get device type and
    UC, to print the possible devices and to terminate it.
    """

    _config: DeviceConfig
    quiet: bool
    filepath: Path
    buffer: list[int]

    # TODO Implement
    # @staticmethod
    # def from_config_string(config: str) -> "Device":
    #     ...

    # TODO Implement
    # @staticmethod
    # def from_config_values(type_: DeviceType, mode: DeviceMode, identifier: int) -> "Device":
    #     config = DeviceConfig(type, mode, identifier)
    #     ...

    def __init__(
        self,
        in_type: int,
        identifier: int,
        filepath: str | None = None,
        in_mode: str = DeviceMode.NONE,
        printer=None,  # FIXME Deprecated, should be removed completely
        quiet: bool = False,
    ):
        type_ = DeviceType(in_type)
        mode = DeviceMode(in_mode)
        self._config = DeviceConfig(type_, identifier, mode)
        self.quiet = quiet

        self.buffer = []

        if self._config.type == DeviceType.DISK:
            assert filepath is not None
            assert self._config.mode != DeviceMode.NONE
            self.filepath = Path(filepath)
            if self._config.mode == DeviceMode.READ:
                self._read_file_into_buffer()
            elif self._config.mode == DeviceMode.WRITE:
                self.filepath.unlink(missing_ok=True)
        elif self._config.type == DeviceType.PRINTER:
            pass
        elif self._config.type == DeviceType.KEYBOARD:
            self.buffer = []

    @property
    def type(self) -> DeviceType:
        return self._config.type

    @property
    def mode(self) -> DeviceMode:
        return self._config.mode

    @property
    def identifier(self) -> int:
        return self._config.identifier

    def is_readable(self):
        return self._config.is_readable

    def is_writable(self):
        return self._config.is_writable

    def has_buffer(self):
        return self._config.has_buffer

    def get_data(self, keyboard_timeout_seconds: int = 0) -> int:
        """Get data from the device and return it, the limit to be
        returned is one byte (or two nibbles)"""

        msb = 0
        lsb = 0

        if not self.is_readable():
            raise MvnError(f"Unreadable device {self._config.type.name}")

        if self._config.type == DeviceType.KEYBOARD and len(self.buffer) < 2:
            try:
                self.buffer.extend(self._timeout_input(keyboard_timeout_seconds))
            except TimeoutError:
                pass
            except EOFError:
                # TODO Assess what is the expected behaviour in this case
                pass

        if len(self.buffer) >= 1:
            msb = self.buffer.pop(0)
            if len(self.buffer) >= 1:
                lsb = self.buffer.pop(0)

        return (msb << 8) + lsb

    @staticmethod
    def _timeout_input(seconds: int = 0) -> bytes:
        def timeout(signal_number, stack_frame) -> None:
            raise TimeoutError("Time limit exceeded")

        signal.signal(signal.SIGALRM, timeout)

        signal.alarm(seconds)
        keyboard_input = input()
        signal.alarm(0)  # Disables alarm if input is received in time
        return keyboard_input.encode("ascii")

    def put_data(self, value: int) -> None:
        """Put given data to the device, the limit to be put is one
        byte (or two nibbles)"""

        if not self.is_writable():
            raise MvnError("Unwritable device")

        word = Word(value)

        if self._config.type == DeviceType.DISPLAY:
            print(word.as_ascii())
        elif self._config.type == DeviceType.PRINTER:
            pass
        elif self._config.type == DeviceType.DISK:
            with open(self.filepath, "ab") as file:
                file.write(word.value.to_bytes(2, byteorder="big"))

    def append_buffer(self) -> None:
        if not self.is_readable() or self.type != 3:
            raise MvnError("Unreadable device")
        self._read_file_into_buffer()

    def clean_buffer(self) -> None:
        if not self.has_buffer():
            raise MvnError("No buffer to be cleaned")
        self.buffer = []

    def close(self) -> None:
        pass

    def get_type(self) -> int:
        """Return device type"""
        return self.type

    def get_uc(self) -> int:
        """Return device UC"""
        return self.identifier

    @staticmethod
    def show_available() -> None:
        """Print the possible devices"""
        print("Tipos de dispositivos disponíveis:")
        print("   Teclado    -> 0")
        print("   Monitor    -> 1")
        print("   Impressora -> 2")
        print("   Disco      -> 3")

    def _read_file_into_buffer(self) -> None:
        with open(self.filepath, "rb") as file:
            self.buffer.extend(file.read())
