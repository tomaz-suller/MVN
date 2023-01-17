from enum import IntEnum, unique

from dotenv import dotenv_values

_CONFIG: dict[str, str] = dotenv_values()


@unique
class Instruction(IntEnum):
    JUMP = "JUMP"  # noqa: E221
    JUMP_IF_ZERO = "JUMP_IF_ZERO"  # noqa: E221
    JUMP_IF_NEGATIVE = "JUMP_IF_NEGATIVE"  # noqa: E221
    LOAD_VALUE = "LOAD_VALUE"  # noqa: E221
    ADD = "ADD"  # noqa: E221
    SUBTRACT = "SUBTRACT"  # noqa: E221
    MULTIPLY = "MULTIPLY"  # noqa: E221
    DIVIDE = "DIVIDE"  # noqa: E221
    LOAD = "LOAD"  # noqa: E221
    MEMORY = "MEMORY"  # noqa: E221
    SUBROUTINE = "SUBROUTINE"  # noqa: E221
    RETURN_FROM_SUBROTINE = "RETURN_FROM_SUBROTINE"  # noqa: E221
    HALT_MACHINE = "HALT_MACHINE"  # noqa: E221
    GET_DATA = "GET_DATA"  # noqa: E221
    PUT_DATA = "PUT_DATA"  # noqa: E221
    OPERATING_SYSTEM = "OPERATING_SYSTEM"  # noqa: E221

    # TODO Check if it is possible to access the variant name in `__new__`
    # to remove unecessary string assignment
    def __new__(cls, instruction_name: str):
        value = int(_CONFIG[f"VALUE_{instruction_name}"], 16)
        obj = int().__new__(cls, value)
        obj._value_ = value
        return obj
