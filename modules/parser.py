import sys
from typing import TextIO

from modules.error import ERR_HEADER
from modules.instruction import Instruction

IPPCODE_NAME = "IPPcode24"


class Stats:
    def __init__(self) -> None:
        self.loc = 0
        self.comments = 0
        self.labels = 0
        self.jumps = 0
        self.fwjumps = 0
        self.backjumps = 0


class IPPcodeParser():

    def __init__(self, stream: TextIO = sys.stdin) -> None:
        self.stream = stream
        self.instruction_list = []
        self.stats = Stats()
        pass

    def nextline(self) -> str:
        """
        Read next non-empty line from stream and strip it from `' '` and
        `'\\t'`

        non-empty contains anything else than whitespace and comment
        """
        for line in self.stream:
            if (comment_start := line.find("#")) != -1:  # Remove comments
                self.stats.comments += 1
                line = line[:comment_start]
            line = line.strip(" \t\n")  # Remove whitespace around
            if line:  # If still not empty, return
                return line

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
            self.stats.loc += 1

    def get_internal_repr(self) -> list[Instruction]:
        """
        Return internal representation of the provided IPPcode
        """
        return self.instruction_list
