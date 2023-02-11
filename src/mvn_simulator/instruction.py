from enum import IntEnum, unique

from dotenv import dotenv_values

_CONFIG: dict[str, str] = dotenv_values()


@unique
class Instruction(IntEnum):
    JUMP = "JUMP"
    JUMP_IF_ZERO = "JUMP_IF_ZERO"
    JUMP_IF_NEGATIVE = "JUMP_IF_NEGATIVE"
    LOAD_VALUE = "LOAD_VALUE"
    ADD = "ADD"
    SUBTRACT = "SUBTRACT"
    MULTIPLY = "MULTIPLY"
    DIVIDE = "DIVIDE"
    LOAD = "LOAD"
    MEMORY = "MEMORY"
    SUBROUTINE = "SUBROUTINE"
    RETURN_FROM_SUBROTINE = "RETURN_FROM_SUBROTINE"
    HALT_MACHINE = "HALT_MACHINE"
    GET_DATA = "GET_DATA"
    PUT_DATA = "PUT_DATA"
    OPERATING_SYSTEM = "OPERATING_SYSTEM"

    # TODO Check if it is possible to access the variant name in `__new__`
    # to remove unecessary string assignment
    def __new__(cls, instruction_name: str):
        value = int(_CONFIG[f"VALUE_{instruction_name}"], 16)
        obj = int().__new__(cls, value)
        obj._value_ = value
        return obj
