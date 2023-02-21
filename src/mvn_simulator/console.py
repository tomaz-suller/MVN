import code
import glob
import os
import readline
import shlex
import tempfile
from codeop import CommandCompiler
from typing import Union

from .monitor import Monitor, MonitorCode, MonitorOperation


class MonitorCommandCompiler(CommandCompiler):  # pylint: disable=too-few-public-methods
    def __call__(self, source: str, *args, **kwargs) -> Union[MonitorCode, None]:
        tokens = shlex.split(source)
        operation_str, arguments = tokens[0], tokens[1:]
        try:
            operation = MonitorOperation(operation_str[0])
        except ValueError as exc:
            raise SyntaxError(f"Unknown operation `{operation_str}`") from exc

        if len(arguments) > operation.argument_count:
            raise SyntaxError(
                f"Too many arguments specified for operation `{operation}`; "
                f"expected {operation.argument_count} but got {len(arguments)}"
            )
        if len(arguments) < operation.argument_count:
            return None

        return MonitorCode(operation, arguments).parse_arguments()


class MonitorConsole(code.InteractiveConsole):
    BANNER = f"""
    =======================================================================
                Escola Politécnica da Universidade de São Paulo
              Computer and Digital Systems Engineering Department
                        PCS3616 - Systems's Programming

                       MVN - von Neumann Machine Simulator

                               All rights reserved
    =======================================================================
    For available commands, enter `{MonitorOperation.PRINT_HELP.value}`
    or enter `Ctrl-D` to exit
    """

    def __init__(self, monitor: Monitor):
        super().__init__()
        self.monitor = monitor
        self.compile = MonitorCommandCompiler()

    def runcode(self, code: MonitorCode):  # pylint: disable=redefined-outer-name
        try:
            self.monitor.execute(code)
        except SystemExit:
            raise
        except:  # pylint: disable=bare-except # noqa: E722
            self.showtraceback()


def completer(text: str, state: int) -> Union[str, None]:
    tokens = readline.get_line_buffer().split()
    if tokens:
        partial_path = tokens[-1] if len(tokens) > 1 else ""
        return path_completer(partial_path, state)
    return operation_completer(text, state)


def path_completer(text: str, state: int) -> Union[str, None]:
    try:
        return [os.path.basename(path) for path in glob.glob(text + "*")][state]
    except IndexError:
        return None


def operation_completer(_, state: int) -> Union[str, None]:
    options = [operation.value for operation in MonitorOperation] + [None]
    return options[state]


if __name__ == "__main__":
    import argparse

    readline.parse_and_bind("tab: complete")
    readline.set_completer(completer)
    readline.set_auto_history(True)

    try:
        with open(".mvnhistory_filepath", encoding="utf8") as f:
            history_filepath = f.read().strip()
            assert os.path.exists(history_filepath)
    except (FileNotFoundError, AssertionError):
        with tempfile.NamedTemporaryFile(prefix="mvnhistory-", delete=False) as f:
            history_filepath = f.name
        with open(".mvnhistory_filepath", "w", encoding="utf8") as f:
            f.write(history_filepath)

    readline.read_history_file(history_filepath)

    parser = argparse.ArgumentParser(description="MVN execution parameters")
    parser.add_argument(
        "-s",
        "--step-limit",
        action="store",
        type=int,
        required=False,
        help="The maximum number of steps to be considered not an infinite loop",
        default=10000,
    )
    parser.add_argument(
        "-i",
        "--time_interrupt",
        action="store",
        type=int,
        required=False,
        help="Tha maximum number of steps before making a time interruption. If not given, time interruptins will be disabled",
    )
    parser.add_argument(
        "-t",
        "--timeout_input",
        action="store",
        type=int,
        required=False,
        help="The maximun time to wait for user keyboard input in miliseconds. If not given, time timeout will be disabled",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_false",
        required=False,
        help="When active the MVN enters in silent mode and will no show debug messages during execution",
        default=True,
    )
    cli_args = parser.parse_args()
    step_limit = cli_args.step_limit
    simulator_args = [
        cli_args.time_interrupt is not None,
        cli_args.time_interrupt,
        cli_args.timeout_input,
        cli_args.quiet,
    ]

    console = MonitorConsole(Monitor(step_limit, *simulator_args))
    console.interact(banner=MonitorConsole.BANNER)

    readline.write_history_file(history_filepath)
