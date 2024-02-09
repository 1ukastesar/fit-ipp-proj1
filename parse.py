#!/usr/bin/env python3.10

import argparse
import re
import signal
import sys
from typing import TextIO
from xml.etree import ElementTree

ERR_PARAM    = 10
ERR_HEADER   = 21
ERR_OPCODE   = 22
ERR_OTHER    = 23
ERR_INTERNAL = 99
ERR_SIGINT   = 130

IPPCODE_NAME = "IPPcode24"


# Handle SIGINT (produced by Ctrl+C and raises KeyboardInterrupt)
# it prints awful traceback everytime
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

        if len(sys.argv) > 2:  # e.g. file --help --other -> 3 arguments
            self.error("--help can't be combined with other arguments")
        return super().print_help(file)


class InstructionArgumentError(Exception):
    pass


class InstructionBadArgumentCountError(Exception):
    pass


class InstructionPattern:

    var_name = "([a-zA-Z_\-\$&%*!?][a-zA-Z0-9_\-\$&%\*!?]*)$"
    label = re.compile("^" + var_name)
    var   = re.compile("^(GF|LF|TF)@" + var_name)
    const = re.compile("^(int|bool|string|nil)@(.*)$")


class Instruction():

    pattern = InstructionPattern()

    def var(self, arg: str) -> tuple[str, str]:
        """
        <var> ::= var
        """
        if (self.pattern.var.match(arg)):
            return "var", arg
        else:
            raise InstructionArgumentError

    def symb(self, arg: str) -> tuple[str, str]:
        """
        <symb> ::= <var> | <const>
        """
        if (match := self.pattern.var.match(arg)):
            return "var", arg
        elif (match := self.pattern.const.match(arg)):
            return match.group(1), match.group(2)
        else:
            raise InstructionArgumentError

    def label(self, arg: str) -> tuple[str, str]:
        """
        <label> ::= label
        """
        if (match := self.pattern.label.match(arg)):
            return "label", match.group(0)
        else:
            raise InstructionArgumentError

    def type(self, arg: str) -> tuple[str, str]:
        """
        <type> ::= int | string | bool
        """
        if arg in ["int", "string", "bool"]:
            return "type", arg
        else:
            raise InstructionArgumentError

    # INSTRUCTION DEFINITIONS

    def MOVE(self, args: list[str]):
        """
        MOVE <var> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb = self.symb(args[1])

        return [var, symb]

    def CREATEFRAME(self, args: list[str]):
        """
        CREATEFRAME
        """
        if args:
            raise InstructionBadArgumentCountError

    def PUSHFRAME(self, args: list[str]):
        """
        PUSHFRAME
        """
        if args:
            raise InstructionBadArgumentCountError

    def POPFRAME(self, args: list[str]):
        """
        POPFRAME
        """
        if args:
            raise InstructionBadArgumentCountError

    def DEFVAR(self, args: list[str]):
        """
        DEFVAR <var>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.var(args[0])]

    def CALL(self, args: list[str]):
        """
        CALL <label>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.label(args[0])]

    def RETURN(self, args: list[str]):
        """
        RETURN
        """
        if args:
            raise InstructionBadArgumentCountError

    def PUSHS(self, args: list[str]):
        """
        PUSHS <symb>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.symb(args[0])]

    def POPS(self, args: list[str]):
        """
        POPS <var>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.var(args[0])]

    def ADD(self, args: list[str]):
        """
        ADD <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def SUB(self, args: list[str]):
        """
        SUB <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def MUL(self, args: list[str]):
        """
        MUL <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def IDIV(self, args: list[str]):
        """
        IDIV <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def LT(self, args: list[str]):
        """
        LT <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def GT(self, args: list[str]):
        """
        GT <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def EQ(self, args: list[str]):
        """
        EQ <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def AND(self, args: list[str]):
        """
        AND <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def OR(self, args: list[str]):
        """
        OR <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def NOT(self, args: list[str]):
        """
        NOT <var> <symb> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def INT2CHAR(self, args: list[str]):
        """
        INT2CHAR <var> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb = self.symb(args[1])

        return [var, symb]

    def STRI2INT(self, args: list[str]):
        """
        STRI2INT <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def READ(self, args: list[str]):
        """
        READ <var> <type>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        type = self.type(args[1])

        return [var, type]

    def WRITE(self, args: list[str]):
        """
        WRITE <symb>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.symb(args[0])]

    def CONCAT(self, args: list[str]):
        """
        CONCAT <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def STRLEN(self, args: list[str]):
        """
        STRLEN <var> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb = self.symb(args[1])

        return [var, symb]

    def GETCHAR(self, args: list[str]):
        """
        GETCHAR <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def SETCHAR(self, args: list[str]):
        """
        SETCHAR <var> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [var, symb1, symb2]

    def TYPE(self, args: list[str]):
        """
        TYPE <var> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb = self.symb(args[1])

        return [var, symb]

    def LABEL(self, args: list[str]):
        """
        LABEL <label>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.label(args[0])]

    def JUMP(self, args: list[str]):
        """
        JUMP <label>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.label(args[0])]

    def JUMPIFEQ(self, args: list[str]):
        """
        JUMPIFEQ <label> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        label = self.label(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [label, symb1, symb2]

    def JUMPIFNEQ(self, args: list[str]):
        """
        JUMPIFNEQ <label> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        label = self.label(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])

        return [label, symb1, symb2]

    def EXIT(self, args: list[str]):
        """
        EXIT <symb>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.symb(args[0])]

    def DPRINT(self, args: list[str]):
        """
        DPRINT <symb>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        return [self.symb(args[0])]

    def BREAK(self, args: list[str]):
        """
        BREAK
        """
        if args:
            raise InstructionBadArgumentCountError

    # INSTRUCTION DEFINITIONS END

    def __init__(self, opcode: str, args: list[str]) -> None:
        """
        Try to build an instruction from opcode and arguments
        """
        try:
            self.args = getattr(self, opcode.upper())(args)
            self.opcode = opcode
        except AttributeError:
            sys.exit(ERR_OPCODE)
        except (InstructionArgumentError, InstructionBadArgumentCountError):
            sys.exit(ERR_OTHER)

    def __str__(self) -> str:
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

    def parse(self) -> None:
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

    def __init__(self) -> None:
        """
        Initialize XMLBuilder with "program" root element
        """
        self.program = ElementTree.Element("program", attrib={"language": IPPCODE_NAME})
        self.order = 0

    def get_instruction_order(self) -> int:
        """"
        Return order of the next instruction
        """
        self.order += 1
        return self.order

    def build_instruction(self, opcode: str, args: list[tuple[str, str]]) -> ElementTree.Element:
        """
        Build a single instruction element
        """
        instruction = ElementTree.Element("instruction", attrib={"order": str(self.get_instruction_order()), "opcode": opcode})
        try:
            for i, arg in enumerate(args, start=1):
                ElementTree.SubElement(instruction, f"arg{i}", attrib={"type" : arg[0]}).text = arg[1]
        except TypeError:
            pass
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
