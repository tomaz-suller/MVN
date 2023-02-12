from dataclasses import dataclass
from enum import Enum, unique
from pathlib import Path
import sys

from .mvn import Mvn
from .utils import MvnError


COMMENT_DELIMITER = ';'


def remove_comment_from_line(line: str) -> str:
    return line.split(COMMENT_DELIMITER)[0].strip()


def yes_to_bool(string: str) -> bool:
    return string.lower() in ['y', 'yes', 'sim', 's']


@unique
class MonitorOperation(str, Enum):
    RESET_SIMULATOR = 'i'
    LOAD_PROGRAM = 'p'
    EXECUTE_PROGRAM = 'r'
    # TOGGLE_DEBUG = 'b'
    CONFIGURE_IO = 's'
    PRINT_REGISTERS = 'g'
    PRINT_MEMORY = 'm'
    PRINT_HELP = 'h'
    EXIT = 'x'

    @property
    def argument_count(self) -> int:
        if self == MonitorOperation.EXECUTE_PROGRAM:
            return 3
        if self == MonitorOperation.PRINT_MEMORY:
            return 2
        if self == MonitorOperation.LOAD_PROGRAM:
            return 1
        return 0


@dataclass
class MonitorCode:
    operation: MonitorOperation
    arguments: list

    def parse_arguments(self) -> "MonitorCode":
        arguments = self.arguments
        if self.operation == MonitorOperation.EXECUTE_PROGRAM:
            arguments = [
                int(self.arguments[0], 16),
                yes_to_bool(self.arguments[1]),
                yes_to_bool(self.arguments[2]),
            ]
        if self.operation == MonitorOperation.PRINT_MEMORY:
            arguments = sorted(int(arg, 16) for arg in self.arguments)
        if self.operation == MonitorOperation.LOAD_PROGRAM:
            arguments = [Path(arguments[0])]
        return MonitorCode(self.operation, arguments)


# TODO Implement debug mode
class Monitor:
    simulator: Mvn
    device_config_path: Path = Path('disp.lst')
    _simulator_args: list
    _should_continue: bool = True
    _program_loaded: bool = False

    def __init__(self, step_limit: int, *simulator_args):
        self.simulator = Mvn(*simulator_args)
        self.step_limit = step_limit
        self._simulator_args = simulator_args
        # FIXME Move device initialization out of simulator
        if self.device_config_path.exists():
            self.simulator.create_disp()

    def execute(self, code: MonitorCode) -> None:
        function_map = {
            MonitorOperation.RESET_SIMULATOR: self.reset,
            MonitorOperation.LOAD_PROGRAM: self.load,
            MonitorOperation.EXECUTE_PROGRAM: self.run,
            MonitorOperation.CONFIGURE_IO: self.devices,
            MonitorOperation.PRINT_REGISTERS: self.print_state,
            MonitorOperation.PRINT_MEMORY: self.print_memory,
            MonitorOperation.PRINT_HELP: self.help,
            MonitorOperation.EXIT: self.exit,
        }
        func = function_map[code.operation]
        func(*code.arguments)

    # TODO Improve help with multiline explanations, perhaps using
    # function dosctrings directly
    @staticmethod
    def help() -> None:
        print("""
            Commands may take arguments, in which case they may all be passed in the
            same line along with the command, or in subsequent lines.

            Commands:
                i                   Restart simulator.
                p <file>            Load program stored in <file>.
                r <addr>            Execute program from memory address <addr>;
                  <printregs>       Set <printregs> to 'y' to print register values,
                  <stepbystep>      and <setpbystep> to pause, after each instruction.
                s                   Open I/O device menu.
                g                   Print register contents.
                m <start> <end>     Print memory content from <start> to <end> address.
                h                   Print this help menu.
                x                   Exit.
        """)

    def reset(self) -> None:
        # TODO Add reset function to simulator
        self.simulator = Mvn(*self._simulator_args)

    def load(self, filepath: Path) -> None:
        """Open given file, read it, separate memory and addresses and
        send them to the MVN memory"""

        with open(filepath, encoding='utf8') as f:
            machine_program = [
                line
                for line in (
                    remove_comment_from_line(raw_line).split()
                    for raw_line in f.readlines()
                    if raw_line
                )
                if line
            ]

        if any((len(machine_code) != 2 for machine_code in machine_program)):
            raise MvnError(
                "malformed file: line contians more than two values "
                "(all lines should be written {{address}}\\s+{{value}} in hex)"
            )

        self.simulator.set_memory(machine_program)
        self._program_loaded = True

    def run(self, initial_address: int, print_registers: bool, step_by_step: bool) -> None:
        if not self._program_loaded:
            raise MvnError("cannot start execution with no loaded program")
        # TODO Refactor simulator to encapsulate initial address config
        self.simulator.IC.set_value(initial_address)
        steps = 0
        while self._should_continue:
            self.step()
            steps += 1
            if steps > self.step_limit:
                self._should_continue = False
            if print_registers:
                if steps == 1:
                    self.print_register_heading()
                print(self.simulator.state_str())
                if step_by_step:
                    input()

    def step(self) -> None:
        self._should_continue = self.simulator.step()

    # TODO Implement devices menu
    def devices(self) -> None:
        raise NotImplementedError("Devices menu still under development")

    def print_state(self) -> None:
        self.print_register_heading()
        print(self.simulator.state_str)

    def print_memory(self, begin: int, end: int) -> None:
        dump_filepath = None
        dump_filepath_str = input('dump filepath (press enter to print to terminal): ')
        if dump_filepath_str:
            dump_filepath = Path(dump_filepath_str)
        self.simulator.dump_memory(begin, end, dump_filepath)

    @staticmethod
    def exit() -> None:
        sys.exit()

    # TODO Implement
    def add_devices_from_config(self) -> None:
        ...

    @staticmethod
    def print_register_heading() -> None:
        print(" MAR  MDR  IC   IR   OP   OI   AC ")
        print("---- ---- ---- ---- ---- ---- ----")

# def run_dbg(mvn, goon):
#     """Run the code in debugger mode, in this mode vals and sbs are not
#     needed. The debugger mode has it's own instruction set, to execute
#     debugging operations, see bdg_help() for complete guide"""

#     print(c3po("start"))
#     print(c3po("dbg_comm"))
#     print(c3po("dbg_help"))
#     print(c3po("reg_head"))
#     step = True
#     while goon:
#         if step or mvn.IC.get_value() in breakpoints:
#             step = False
#             out = False
#             while not out:
#                 read = input("(dgb) ").split(" ")
#                 if not len(read) == 0:
#                     switch(read[0])
#                     if case("c"):
#                         out = True
#                     elif case("s"):
#                         step = True
#                         out = True
#                     elif case("b"):
#                         if len(read) > 1:
#                             for breaks in read[1:]:
#                                 try:
#                                     breakpoints.append(int(breaks, 16))
#                                 except:
#                                     print(c3po("break_hex"))
#                         else:
#                             print(c3po("no_addr"))
#                     elif case("x"):
#                         out = True
#                         goon = False
#                     elif case("h"):
#                         print(c3po("dbg_help"))
#                     elif case("r"):
#                         if len(read) == 3:
#                             try:
#                                 if read[1] not in [
#                                     "MAR",
#                                     "MDR",
#                                     "IC",
#                                     "IR",
#                                     "OP",
#                                     "OI",
#                                     "AC",
#                                 ]:
#                                     print(c3po("reg_inv"))
#                                 elif read[1] == "MAR":
#                                     mvn.MAR.set_value(int(read[2], 16))
#                                 elif read[1] == "MDR":
#                                     mvn.MDR.set_value(int(read[2], 16))
#                                 elif read[1] == "IC":
#                                     mvn.IC.set_value(int(read[2], 16))
#                                 elif read[1] == "IR":
#                                     mvn.IR.set_value(int(read[2], 16))
#                                 elif read[1] == "OP":
#                                     mvn.OP.set_value(int(read[2], 16))
#                                 elif read[1] == "OI":
#                                     mvn.OI.set_value(int(read[2], 16))
#                                 elif read[1] == "AC":
#                                     mvn.AC.set_value(int(read[2], 16))
#                             except:
#                                 print(c3po("val_hex"))
#                     elif case("a"):
#                         mvn.mem.set_value(int(read[1], 16), int(read[2], 16))
#                     elif case("e"):
#                         print(c3po("reg_head"))
#                         print(mvn.print_state())
#                     elif case("m"):
#                         mvn.dump_memory(int(read[1], 16), int(read[2], 16))
#                     else:
#                         print(c3po("no_rec"))
#         goon = mvn.step() and goon
#         print(mvn.print_state())


# if __name__ == '__main__':

    # Here starts the main code for the MVN's user interface, this will
    # look like a cmd to the user, but operating the MVN class

    # First thing to be done is inicialize our MVN
    # mvn: Mvn = inicialize(time_interrupt, time_limit, timeout, quiet)
    # This loop will deal with the MVN's interface commands
    # while True:
    #     command = input("\n> ")
    #     command = clean(command)
    #     # No action to be taken if nothing was typed
    #     if command:
    #         switch(command[0])
    #         # Display the available devices and give options to add or remove
    #         if case("s"):
    #             print(c3po("dev_head"))
    #             mvn.print_devs()
    #             switch(input(c3po("dev_deal")))
    #             if case("a"):
    #                 mvn.show_available_devs()
    #                 dtype = input(c3po("dev_type"))
    #                 try:
    #                     dtype = int(dtype)
    #                     go = True
    #                 except:
    #                     print(c3po("inv_val"))
    #                     go = False
    #                 if go:
    #                     UC = input(c3po("dev_UL"))
    #                     try:
    #                         UC = int(UC)
    #                         go = True
    #                     except:
    #                         print(c3po("inv_val"))
    #                         go = False
    #                 if go:
    #                     if dtype == 2:
    #                         name = input(c3po("print_name"))
    #                         mvn.new_dev(dtype, UC, printer=name)
    #                     elif dtype == 3:
    #                         file = input(c3po("file_name"))
    #                         met = input(c3po("op_mode"))
    #                         mvn.new_dev(dtype, UC, file, met)
    #                     else:
    #                         mvn.new_dev(dtype, UC)
    #                     print(c3po("dev_add", (str(dtype), str(UC))))
    #             elif case("r"):
    #                 mvn.show_available_devs()
    #                 dtype = input(c3po("dev_type"))
    #                 try:
    #                     dtype = int(dtype)
    #                     go = True
    #                 except:
    #                     print(c3po("inv_val"))
    #                     go = False
    #                 if go:
    #                     UC = input(c3po("dev_UL"))
    #                     try:
    #                         UC = int(UC)
    #                         go = True
    #                     except:
    #                         print(c3po("inv_val"))
    #                         go = False
    #                 if go:
    #                     mvn.rm_dev(dtype, UC)
