import os.path
import subprocess


class MvnError(Exception):
    """Error class"""


def hex_zfill(value: int, width: int, upper: bool = True) -> str:
    string = hex(value)[2:].zfill(width)
    return string.upper() if upper else string


def valid_value(num, MIN, MAX):
    """Test if argument is between MIN and MAX, raise error"""
    if not (MIN <= num and num <= MAX):
        raise MvnError("Incompatible size")


def valid_instru(num):
    """Test if argument is 1,2,4,5,6 or 7, A, B, C, D, raise error"""
    if num not in [1, 2, 4, 5, 6, 7, 0xA, 0xB, 0xC, 0xD]:
        raise MvnError("Incompatible instruction")


def valid_type(val):
    """Test if argument is between 0 and 4, raise error"""
    if not (val >= 0 and val <= 3):
        raise MvnError("Incompatible type")


def valid_file(file):
    """Test if the given file exists, raise error"""
    if not (os.path.exists(file)):
        raise MvnError("File does not exist")


def valid_rwb(rwb):
    """Test if given rwb is valid, raise error"""
    if rwb not in ["e", "l", "b"]:
        raise MvnError("Incompatible parameter")


def valid_printer(printer):
    """Test if the printer exists in OS, raise error"""
    try:
        subprocess.check_output(["lpstat", "-p", printer])
    except:
        raise MvnError("Impressora invalida")


def clean(line):
    """Separate an given string by spaces and remove substrings with
    no content"""
    res = []
    line = line.split(" ")
    for word in line:
        if word != "":
            res.append(word)
    return res
