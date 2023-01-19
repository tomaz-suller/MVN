import io
from pathlib import Path

import pytest

from mvn_simulator.device import Device, DeviceMode, DeviceType
from mvn_simulator.utils import MvnError


class TestDeviceMode:
    def test_values(self):
        assert DeviceMode.READ == "l"
        assert DeviceMode.WRITE == "e"

    def test_parse(self):
        assert DeviceMode("l") == DeviceMode.READ
        assert DeviceMode("e") == DeviceMode.WRITE
        with pytest.raises(ValueError, match="is not a valid"):
            _ = DeviceMode("foobar")

    def test_open_mode(self):
        assert DeviceMode.READ.open_mode == "r"
        assert DeviceMode.WRITE.open_mode == "wb"
        with pytest.raises(ValueError, match="doesn't allow opening files"):
            _ = DeviceMode.NONE.open_mode


class TestDeviceType:
    def test_value(self):
        assert DeviceType.KEYBOARD == 0
        assert DeviceType.DISPLAY == 1
        assert DeviceType.PRINTER == 2
        assert DeviceType.DISK == 3

    def test_parse(self):
        assert DeviceType(0) == DeviceType.KEYBOARD
        assert DeviceType(1) == DeviceType.DISPLAY
        assert DeviceType(2) == DeviceType.PRINTER
        assert DeviceType(3) == DeviceType.DISK
        with pytest.raises(ValueError, match="is not a valid"):
            _ = DeviceType(4)


# Odd number of characters on purpose
# to test behaviour at the end of the string
TEST_STRING = "Hello, World!"


class TestDevice:
    @staticmethod
    @pytest.fixture
    def filepath(tmp_path: Path) -> Path:
        path = tmp_path / "tmp.dat"
        path.touch()
        return path

    @staticmethod
    @pytest.fixture
    def keyboard() -> Device:
        return Device(DeviceType.KEYBOARD, 0)

    @staticmethod
    @pytest.fixture
    def display() -> Device:
        return Device(DeviceType.DISPLAY, 0)

    @staticmethod
    def disk(mode: DeviceMode, filepath: Path) -> Device:
        return Device(DeviceType.DISK, 0, mode, filepath=filepath)

    @staticmethod
    @pytest.fixture
    def read_disk(filepath: Path):
        with open(filepath, "w", encoding="ascii") as file:
            file.write(TEST_STRING)
        return TestDevice.disk(DeviceMode.READ, filepath)

    @staticmethod
    @pytest.fixture
    def write_disk(filepath: Path):
        return TestDevice.disk(DeviceMode.WRITE, filepath)

    @staticmethod
    def encode(literal: bytes) -> int:
        return int.from_bytes(literal, byteorder="big")

    class TestConstructor:
        def test_keyboard(self):
            device = Device(0, 0)
            assert device.type == DeviceType.KEYBOARD
            assert device.identifier == 0
            assert device.mode == DeviceMode.NONE

        def test_display(self):
            device = Device(1, 0)
            assert device.type == DeviceType.DISPLAY
            assert device.identifier == 0
            assert device.mode == DeviceMode.NONE

        @pytest.mark.parametrize(
            "mode_str,mode", [("e", DeviceMode.WRITE), ("l", DeviceMode.READ)]
        )
        def test_valid_disk(self, mode_str: str, mode: DeviceMode, filepath: Path):
            device = Device(3, 0, mode_str, filepath=filepath)
            assert device.type == DeviceType.DISK
            assert device.identifier == 0
            assert device.mode == mode

        def test_invalid_disk(self):
            with pytest.raises(AssertionError):
                _ = Device(3, 0, filepath=Path("."))
            with pytest.raises(AssertionError):
                _ = Device(3, 0, DeviceMode.WRITE)

    class TestRead:
        @pytest.mark.parametrize("device_name", ["keyboard", "read_disk"])
        def test_read_on_readable(self, request, monkeypatch, device_name: str):
            device: Device = request.getfixturevalue(device_name)
            if device.type == DeviceType.KEYBOARD:
                monkeypatch.setattr("sys.stdin", io.StringIO(TEST_STRING))
            assert device.get_data() == TestDevice.encode(b"He")
            assert device.get_data() == TestDevice.encode(b"ll")
            assert device.get_data() == TestDevice.encode(b"o,")
            assert device.get_data() == TestDevice.encode(b" W")
            assert device.get_data() == TestDevice.encode(b"or")
            assert device.get_data() == TestDevice.encode(b"ld")
            assert device.get_data() == TestDevice.encode(b"!\0")

        @pytest.mark.parametrize("device_name", ["display", "write_disk"])
        def test_error_on_unreadable(self, request, device_name: str):
            device: Device = request.getfixturevalue(device_name)
            with pytest.raises(MvnError, match="Unreadable device"):
                _ = device.get_data()

        def test_keyboard_timeout_return_value(self, monkeypatch, keyboard: Device):
            def raise_timeout_error(*args, **kwargs):
                raise TimeoutError

            monkeypatch.setattr("sys.stdin", io.StringIO(TEST_STRING))
            monkeypatch.setattr(keyboard, "_timeout_input", raise_timeout_error)
            assert keyboard.get_data() == 0

    class TestWrite:
        def test_write_on_display(self, monkeypatch, display: Device):
            stdout = io.StringIO()
            monkeypatch.setattr("sys.stdout", stdout)
            # Append 0x0 to the end of odd-length strings to make behaviour
            # consistent with `get_value`
            string = TEST_STRING if len(TEST_STRING) % 2 == 0 else TEST_STRING + "\0"
            # `put_data` receives two characters at a time, so we split the
            # string before writing it
            for chars in (string[i : i + 2] for i in range(0, len(string), 2)):
                display.put_data(TestDevice.encode(chars.encode("ascii")))
            result = stdout.getvalue()
            # `print` inserts \n which have to be removed
            result = "".join(result.split("\n"))
            assert result == string

        def test_write_on_disk(self, write_disk: Device):
            # Append 0x0 to the end of odd-length strings to make behaviour
            # consistent with `get_value`
            string = TEST_STRING if len(TEST_STRING) % 2 == 0 else TEST_STRING + "\0"
            # `put_data` receives two characters at a time, so we split the
            # string before writing it
            for chars in (string[i : i + 2] for i in range(0, len(string), 2)):
                write_disk.put_data(TestDevice.encode(chars.encode("ascii")))
            with open(write_disk.filepath, "rb") as file:
                assert file.read() == string.encode("ascii")

        @pytest.mark.parametrize("device_name", ["keyboard", "read_disk"])
        def test_error_on_unwritable(self, request, device_name: str):
            device: Device = request.getfixturevalue(device_name)
            with pytest.raises(MvnError, match="Unwritable device"):
                _ = device.put_data(0x0000)


# class TestDeviceConfig:
#     def

# class TestDevice:

# class TestDeviceConfig:
