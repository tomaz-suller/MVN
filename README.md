# MVN simulator

## What?

This project is an simulator for an simple processor architecture based on the Von Neumenn Machine. It is an extra simple architecture for a single cycle, 16 instructions, 7 register processor. It contains an MVN module, which runs the code, and an MLR, which is an Mounter, Linker and Relocator, to convert and join assembly files.

The MVN will accept files with the ".mvn" extension and the MLR will accept the ".asm". The MVN executes the code, returning no exit, and the MLR creates two files, the ".lst", that describe the mounting processes and rotules in the ".asm" file, and an ".mvn", with the code to be executed by the MVN.

The project also contains the implementation of an monitor to operate all the mechanism simulated in an friendly user interface.

## Motivation

The architecture implemented is used to teach the basic of low level programming to third year students of Computational Engineering from the Polytechnic School of the São Paulo University during the PCS3616-Programming Systems discipline. The use of this language is purely didatic.

## Dependencies

The simulators are coded in Python3, so Its obviously required the machine to have an Python3 interpreter.

Besides that, the libraries used are:

- os
- subprocess

## Details

In MVN/ there are two diagrams named logic_diagram.png and class_diagram.png that represent the implemented code. Besides the classes shown at MVN/class_diagram.png (which are each one in separate files homonymous), we have two aditional files, mvnutils.py, containing generic functions used in other files, and mvnMonitor.py, that contains the interface to run the MVN.

As shown in MVN/logic_diagram.png, the MVN constains 1 LAU, 7 registers, 1 memory and many devices, those are listed and explained below:

### LAU
The LAU in MVN has 6 functions in it:
- is_zero(): this function returns True if the passed argument is 0
- is_neg():this function returns True if the passed argument is lower than 0
- add():return the sum of the two arguments passed
- sub():return the difference of the two arguments passed
- mul():return the product of the two arguments passed
- div():return the integer quocient of the two arguments passed
### Registers
The register have simple functionalities (only gets and sets), they have the following uses:
- MAR: Memory Address Register, it saves the address to be got from the memory
- MDR: Memory Data Register, it saves the value returned from the memory
- IR: Instruction Register, it saves the instruction got at the beggining of each cycle
- OP: OPeration, it saves the operation to be executed at the cycle
- OI: Operand Instruction, it saves the operand of the instruction
- AC: ACmulator, register that is used to save values gotten from various places
- IC: Instruction Counter, it is used to save the address of the next instruction
### Memory
The MVN memory is composed of 0xFFF addresses, the address work the same way as the registers, and can be accessed by pairs of addresses.
### Devices
The devices to be accessed for I/O are of 4 types: keyboard, screen, files and printer. To pre-inicialize the devices list you can set the "disp.lst" file as below:
[type] [UC] [file_name] [rwb] [printer_name]
#### type:
- 0:keyboard
- 1:screen
- 2:file
- 3:printer
#### UC:
It's the Unit Code, it's an unique number for each device in each type
#### file_name (optional):
Only to be set when type=2, it's the name of the file to be read/writen
#### rwb:
Only to be set when type=2, it's the mode to open the file
- e:to be writen
- l:to be read
- b:both
#### printer_name:
Only to be set when type=3, it's the printer name on the system

## Programming

### To MVN

The MVN accepts 16 instructions, those are:

| OPCODE | MNEMONIC | function |
| --- | --- | --- |
| 0 | JP |Jumps to the operand address |
| 1 | JZ |Jumps to the operand address if AC is 0 |
| 2 | JN |Jumps to the operand address if AC is negative |
| 3 | LV |Load the operand to AC |
| 4 | AD |Save in AC the value AC+operend |
| 5 | SB |Save in AC the value AC-operend |
| 6 | ML |Save in AC the value AC*operend |
| 7 | DV |Save in AC the value AC/operend |
| 8 | LD |Save in AC the value stored in operand address |
| 9 | MM |Save in the operand address the value AC |
| A | SC |Call subroutine in operand address |
| B | RS |Return the subroutine that started in operand address |
| C | HM |Halt machine |
| D | GD |Save in AC a pair of nibbles from operand device |
| E | PD |Send value in AC to operand device |
| F | SO |Calls the supervisor to deal with errors |


For coding to the MVN, you may write a file (extension ".mvn" preferably) that discribes the inicial state of the memory. To do that you have to set the content of one pair of addresses per line, that is done the following way:

```
XXXX IPPP ;this is a comment
```

Each X, I and P are representing nibbles.

XXXX is the address you're setting, it's value is between 0x0000 and 0x0FFF.

IPPP is the value to be stored in the address, it's between 0x0000 and 0xFFFF, the most significant nibble, I, is the instruction to be executed and the other three, PPP, is the operand.

### To MLR

The MLR code is still on development, when it's finished I'll be writing the coding instructions for it...

## Executing

To execute the simulator you can either deal with the MVN purely or use the mvnMonitor.

To run the MVN purely you should open the Python3 terminal and import the MVN class, as following:

```
cd MVN/
python3
import MVN
#From now own you need to read the code and crack how to use the functions alone
```

To use the mvnMonitor you can run it with Python3 directly or open an Python3 terminal an import it (this way you get the monitor properties), as following:

```
cd MVN/

#Running purely
python3 mvnMonitor

#Running with terminal
python3
import mvnMonitor
```

The MLR code is still on development, when it's finished I'll be writing the executing instructions for it...