#!/usr/bin/env python3.10

import argparse
import sys
import signal
import re

from typing import TextIO
from xml.etree import ElementTree


ERR_PARAM    = 10
ERR_HEADER   = 21
ERR_OPCODE   = 22
ERR_OTHER    = 23
ERR_INTERNAL = 99
ERR_SIGINT   = 130

IPPCODE_NAME = "IPPcode24"

def sigint_handler(signum, frame):
    sys.exit(ERR_SIGINT)


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """
        Override default error handler to change argparse exit code
        """

        self.print_usage(sys.stderr)
        self.exit(ERR_PARAM, '%s: error: %s\n' % (self.prog, message))

    def print_help(self, file=None):
        """
        Override default help handler to make --help
        exclusive with other arguments
        """

        if len(sys.argv) > 2: # e.g. file --help --other -> 3 arguments
            self.error("--help can't be combined with other arguments")
        return super().print_help(file)



class Instruction():
    
    var_name = "([a-zA-Z_\-\$&%*!?][a-zA-Z0-9_\-\$&%\*!?]*)$"
    label = re.compile("^" + var_name)
    var   = re.compile("^(GF|LF|TF)@" + var_name)
    const = re.compile("^(int|bool|string|nil)@(.*)$")

    # patterns = {
    #     "label" : re.compile("^" + var_name),
    #     "var"   : re.compile("^(GF|LF|TF)@" + var_name),
    #     "const" : re.compile("^(int|bool|string|nil)@(.*)$")
    # }

    # def var(self, arg: str) -> tuple[str, str]:
    #     """
    #     <var> ::= var
    #     """
    #     if (self.var.match(arg)):
    #         return "var", arg
    #     else:
    #         return None

    def symb(self, arg: str) -> tuple[str, str]:
        """
        <symb> ::= <var> | <const>
        """
        if (match := self.var.match(arg)):
            return "var", arg
        elif (match := self.const.match(arg)):
            return match.group(1), match.group(2)
        else:
            return None
        

    def MOVE(self, args: list[str]):
        """
        MOVE <var> <symb>
        """
        if len(args) != 2:
            sys.exit(ERR_OTHER)

        var  = self.var.match(args[0])
        symb = self.symb(args[1])
        if not var or not symb:
            sys.exit(ERR_OTHER)
        
        return "MOVE", [("var", var.group(0)), symb]
    
    def CREATEFRAME(self, args: list[str]):
        """
        CREATEFRAME
        """
        if args:
            sys.exit(ERR_OTHER)
        return "CREATEFRAME", []
    
    def PUSHFRAME(self, args: list[str]):
        """
        PUSHFRAME
        """
        if args:
            sys.exit(ERR_OTHER)
        return "PUSHFRAME", []
    
    def POPFRAME(self, args: list[str]):
        """
        POPFRAME
        """
        if args:
            sys.exit(ERR_OTHER)
        return "POPFRAME", []

    def DEFVAR(self, args: list[str]):
        """
        DEFVAR <var>
        """
        if len(args) != 1:
            sys.exit(ERR_OTHER)
        if not self.var.match(args[0]):
            sys.exit(ERR_OTHER)
        return "DEFVAR", [("var", args[0])]

    def __init__(self, opcode: str, args: list[str]):
        try:
            self.opcode, self.args = getattr(self, opcode.upper())(args)
        except AttributeError:
            sys.exit(ERR_OPCODE)

    def __str__(self):
        return f"{self.opcode} {self.args}"


class IPPcodeParser():

    def __init__(self, stream: TextIO = sys.stdin) -> None:
        self.stream = stream
        self.instruction_list = []
        pass

    def nextline(self) -> str:
        """
        Read next non-empty line from stream and strip it from `' '` and
        `'\\t'`
        
        non-empty contains anything else than whitespace and comment
        """
        for line in self.stream:
            stripped_line = line.strip()
            if stripped_line and stripped_line[0] != "#":
                return line.strip(" \t\n")

    def check_header(self) -> None:
        """
        Check header of the input stream
        """
        try:
            if self.nextline().lower() != "." + IPPCODE_NAME.lower():
                sys.exit(ERR_HEADER)
        # Stream contains only whitespace
        except AttributeError:
            sys.exit(ERR_HEADER)

    def parse_instruction(self, line: str) -> Instruction:
        """
        Parse instruction from line
        """
        opcode, *args = line.replace('\t', ' ').split(' ')
        return Instruction(opcode, args)

    def parse(self):
        """
        Parse the input file
        
        for each line, try to parse the instruction 
        and add it to the list of instructions
        """
        self.check_header()
        while (line := self.nextline()):
            self.instruction_list.append(self.parse_instruction(line))
    
    def get_internal_repr(self) -> list[Instruction]:
        """
        Return internal representation of the provided IPPcode
        """
        return self.instruction_list

class XMLBuilder():

    indent_width = 4

    def __init__(self):
        """
        Initialize XMLBuilder with "program" root element
        """
        self.program = ElementTree.Element("program", attrib={"language": IPPCODE_NAME})
        self.order = 0

    def __get_order(self) -> int:
        """"
        Return order of the next instruction
        """
        self.order += 1
        return self.order

    def build_instruction(self, opcode: str, args: list[tuple[str, str]]) -> ElementTree.Element:
        """
        Build a single instruction element
        """
        instruction = ElementTree.Element("instruction", attrib={"order": str(self.__get_order()), "opcode": opcode})
        for i, arg in enumerate(args, start=1):
            ElementTree.SubElement(instruction, f"arg{i}", attrib={"type" : arg[0]}).text = arg[1]
        return instruction

    def build(self, instruction_list: list[Instruction]) -> None:
        """
        Build XML from internal representation
        """
        for instruction in instruction_list:
            self.program.append(self.build_instruction(instruction.opcode, instruction.args))

    def write(self, file=sys.stdout):
        """
        Write internal XML to a file
        """
        ElementTree.indent(self.program, space=" " * self.indent_width)
        xml = ElementTree.tostring(
            self.program, 
            encoding="UTF-8", 
            xml_declaration=True
            ).decode().replace("'", '"')
        print(xml, file=file)

# It can be used as a module or a standalone script
if __name__ == "__main__":

    # Handle KeyboardInterrupt
    signal.signal(signal.SIGINT, sigint_handler)

    # Handle CLI arguments
    argparser = ArgumentParser(description="Parser for IPPcode24")
    args = argparser.parse_args()

    # Parse input
    parser = IPPcodeParser()
    parser.parse()
    instruction_list = parser.get_internal_repr()

    # Build XML from internal representation
    xml = XMLBuilder()
    xml.build(instruction_list)
    xml.write()
