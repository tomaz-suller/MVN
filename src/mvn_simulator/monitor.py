import argparse
import os.path

from .c3po import C3po
from .mvn import Mvn
from .switchcase import *
from .utils import *

parser = argparse.ArgumentParser(description="MVN execution parameters")
parser.add_argument(
    "-l",
    "--language",
    action="store",
    type=str,
    required=False,
    help="Language of the MVN",
    default="pt",
)
parser.add_argument(
    "-s",
    "--max_step",
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
args = parser.parse_args()

# Initializes C3PO
c3po = C3po(args.language if args.language is not None else "pt")

# Define steps limit
time_interrupt = args.time_interrupt is not None
time_limit = args.time_interrupt
timeout = args.timeout_input
quiet = args.quiet
max_step = args.max_step

# These booleans will represent if the code should continue to
# execute (goon), if the register values are to be shown on screen
# (vals), if MVN should be executed step by step (sbs) and if the
# debugger mode is active (dbg)
goon = False
vals = True
sbs = False
dbg = False


def inicialize(time_interrupt, time_limit, timeout, quiet):
    """Start an MVN, check if there is any 'disp.lst' file and
    inicialze the devices in it, return the MVN inicialized"""

    mvn = Mvn(time_interrupt, time_limit, timeout, quiet)
    print(c3po("MVN_ini"))
    if os.path.exists("disp.lst"):
        mvn.create_disp()
        print(c3po("disp_ini_arq"))
    else:
        print(c3po("disp_ini_def"))
    return mvn


def load(name, mvn):
    """Open given file, read it, separate memory and addresses and
    send them to the MVN memory"""

    valid_file(name)
    file = open(name, "r")
    raw = file.read()
    code = ""
    for l in raw:
        if l == "\t":
            code += " "
        else:
            code += l
    code = code.split("\n")
    line = 0
    while line < len(code):
        try:
            code[line] = code[line][: code[line].index(";")]
        except:
            pass
        code[line] = clean(code[line])
        if len(code[line]) != 2:
            if len(code[line]) == 0:
                code.pop(line)
                line -= 1
            else:
                raise ValueError(c3po("big_instru"))
        line += 1
    mvn.set_memory(code)
    print(c3po("loaded", (name)))


def run(mvn, goon, vals, sbs):
    """Run the code normally using mvn method step. Fisrt thing to do
    is define the values of the booleans vals and sbs and then run until
    goon turns false"""

    n_steps = 0
    if vals:
        s = c3po("yes")
    else:
        s = c3po("no")
    try:
        vals = input(c3po("show_regs", (s)))
        vals = vals == "s" or len(vals) == 0
    except:
        vals = True

    if vals:
        if sbs:
            s = c3po("yes")
        else:
            s = c3po("no")
        try:
            sbs = input(c3po("step_by_step", (s)))
            sbs = sbs == c3po("yes")
        except:
            sbs = True
    else:
        sbs = False

    if vals:
        print(c3po("reg_head"))
    while goon:
        goon = mvn.step()
        n_steps += 1
        if vals:
            if sbs:
                read = input(mvn.print_state())
            else:
                print(mvn.print_state())
        if n_steps > max_step:
            print(c3po("infty_loop"))
            goon = False


def run_dbg(mvn, goon):
    """Run the code in debugger mode, in this mode vals and sbs are not
    needed. The debugger mode has it's own instruction set, to execute
    debugging operations, see bdg_help() for complete guide"""

    print(c3po("start"))
    print(c3po("dbg_comm"))
    print(c3po("dbg_help"))
    print(c3po("reg_head"))
    step = True
    while goon:
        if step or mvn.IC.get_value() in breakpoints:
            step = False
            out = False
            while not out:
                read = input("(dgb) ").split(" ")
                if not len(read) == 0:
                    switch(read[0])
                    if case("c"):
                        out = True
                    elif case("s"):
                        step = True
                        out = True
                    elif case("b"):
                        if len(read) > 1:
                            for breaks in read[1:]:
                                try:
                                    breakpoints.append(int(breaks, 16))
                                except:
                                    print(c3po("break_hex"))
                        else:
                            print(c3po("no_addr"))
                    elif case("x"):
                        out = True
                        goon = False
                    elif case("h"):
                        print(c3po("dbg_help"))
                    elif case("r"):
                        if len(read) == 3:
                            try:
                                if read[1] not in [
                                    "MAR",
                                    "MDR",
                                    "IC",
                                    "IR",
                                    "OP",
                                    "OI",
                                    "AC",
                                ]:
                                    print(c3po("reg_inv"))
                                elif read[1] == "MAR":
                                    mvn.MAR.set_value(int(read[2], 16))
                                elif read[1] == "MDR":
                                    mvn.MDR.set_value(int(read[2], 16))
                                elif read[1] == "IC":
                                    mvn.IC.set_value(int(read[2], 16))
                                elif read[1] == "IR":
                                    mvn.IR.set_value(int(read[2], 16))
                                elif read[1] == "OP":
                                    mvn.OP.set_value(int(read[2], 16))
                                elif read[1] == "OI":
                                    mvn.OI.set_value(int(read[2], 16))
                                elif read[1] == "AC":
                                    mvn.AC.set_value(int(read[2], 16))
                            except:
                                print(c3po("val_hex"))
                    elif case("a"):
                        mvn.mem.set_value(int(read[1], 16), int(read[2], 16))
                    elif case("e"):
                        print(c3po("reg_head"))
                        print(mvn.print_state())
                    elif case("m"):
                        mvn.dump_memory(int(read[1], 16), int(read[2], 16))
                    else:
                        print(c3po("no_rec"))
        goon = mvn.step() and goon
        print(mvn.print_state())


# Here starts the main code for the MVN's user interface, this will
# look like a cmd to the user, but operating the MVN class

# First thing to be done is inicialize our MVN
mvn = inicialize(time_interrupt, time_limit, timeout, quiet)
# Show up the header for the MVN
print(c3po("header", ("0.1.0", "2023")))
# Show options available
print(c3po("help"))

# This loop will deal with the MVN's interface commands
while True:
    command = input("\n> ")
    command = clean(command)

    # No action to be taken if nothing was typed
    if command:
        switch(command[0])
        # To reinicialize the MVN is just to inicialize it one more time
        if case("i"):
            mvn = inicialize(time_interrupt, time_limit, timeout, quiet)

        # To load an program, one argument (the file) is required, if
        # it's not given, ask for it, if more are passed, cancel operation
        elif case("p"):
            if len(command) == 1:
                name = input(c3po("inp_file"))
                name = clean(name)
                if len(name) != 1:
                    print(c3po("big_file", (str(len(command)))))
                else:
                    load(name[0], mvn)
                    goon = True
                    pass
            elif len(command) > 2:
                print(c3po("big_file", (str(len(command) - 1))))
            else:
                name = command[1]
                load(name, mvn)
                goon = True

        # To run the program we have to ask the user it's preference
        # on the starting address and call correspondent function to
        # execute the code dependind if the debugger mode is on
        elif case("r"):
            if goon:
                try:
                    mvn.IC.set_value(
                        int(
                            input(
                                c3po(
                                    "inf_IC",
                                    (str(hex(mvn.IC.get_value())[2:]).zfill(4)),
                                )
                            ),
                            16,
                        )
                    )
                except:
                    pass
                if not dbg:
                    run(mvn, goon, vals, sbs)
                else:
                    run_dbg(mvn, goon)
                goon = True
            else:
                print(c3po("cant_run"))

        # Start/stop the debugger mode
        elif case("b"):
            dbg = not dbg
            if dbg:
                print(c3po("deb_on"))
                breakpoints = []
            else:
                print(c3po("deb_off"))

        # Display the available devices and give options to add or remove
        elif case("s"):
            print(c3po("dev_head"))
            mvn.print_devs()
            switch(input(c3po("dev_deal")))
            if case("a"):
                mvn.show_available_devs()
                dtype = input(c3po("dev_type"))
                try:
                    dtype = int(dtype)
                    go = True
                except:
                    print(c3po("inv_val"))
                    go = False
                if go:
                    UC = input(c3po("dev_UL"))
                    try:
                        UC = int(UC)
                        go = True
                    except:
                        print(c3po("inv_val"))
                        go = False
                if go:
                    if dtype == 2:
                        name = input(c3po("print_name"))
                        mvn.new_dev(dtype, UC, printer=name)
                    elif dtype == 3:
                        file = input(c3po("file_name"))
                        met = input(c3po("op_mode"))
                        mvn.new_dev(dtype, UC, file, met)
                    else:
                        mvn.new_dev(dtype, UC)
                    print(c3po("dev_add", (str(dtype), str(UC))))
            elif case("r"):
                mvn.show_available_devs()
                dtype = input(c3po("dev_type"))
                try:
                    dtype = int(dtype)
                    go = True
                except:
                    print(c3po("inv_val"))
                    go = False
                if go:
                    UC = input(c3po("dev_UL"))
                    try:
                        UC = int(UC)
                        go = True
                    except:
                        print(c3po("inv_val"))
                        go = False
                if go:
                    mvn.rm_dev(dtype, UC)

        # Display actual state os the MVN registers
        elif case("g"):
            print(c3po("reg_head"))
            print(mvn.print_state())

        # Display the memmory of the MVN given the start and end addresses
        elif case("m"):
            if len(command) == 3:
                try:
                    start = int(command[1], 16)
                    stop = int(command[2], 16)
                    mvn.dump_memory(start, stop)
                except:
                    print(c3po("val_hex"))
            elif len(command) == 4:
                try:
                    start = int(command[1], 16)
                    stop = int(command[2], 16)
                    mvn.dump_memory(start, stop, command[3])
                except:
                    print(c3po("val_hex"))
            elif len(command) > 4:
                print(c3po("mult_par"))
            else:
                try:
                    start = int(input(c3po("ini_addr")), 16)
                    stop = int(input(c3po("fin_addr")), 16)
                    mvn.dump_memory(start, stop)
                except:
                    print(c3po("val_hex"))

        # Display the available commands
        elif case("h"):
            print(c3po("help"))

        # Exit terminal
        elif case("x"):
            for dev in mvn.devs:
                dev.terminate()
            print(c3po("end"))
            exit()
