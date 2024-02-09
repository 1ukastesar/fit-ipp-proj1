#!/usr/bin/env python3.10

import argparse
import sys
import signal
from typing import TextIO

from xml.etree import ElementTree

ERR_PARAM    = 10
ERR_HEADER   = 21
ERR_OPCODE   = 22
ERR_OTHER    = 23
ERR_INTERNAL = 99
ERR_SIGINT   = 130


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


class IPPcodeParser():

    def __init__(self, stream: TextIO = sys.stdin):
        self.stream = stream
        pass

    def nextline(self) -> str:
        """
        Read next non-empty line from stream and strip it from `' '` and
        `'\\t'` (non-empty contains anything else than whitespace and comment)
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
            if self.nextline().lower() != ".IPPcode24".lower():
                sys.exit(ERR_HEADER)
        # Stream contains only whitespace
        except AttributeError:
            sys.exit(ERR_HEADER)

    def parse_instruction(self, line: str) -> None:
        """
        Parse instruction from line
        """
        pass

    def parse(self):
        self.check_header()
        while (line := self.nextline()):
            self.parse_instruction(line)


class XMLBuilder():

    def __init__(self):
        self.xml = ""
        self.order = 0

    def __get_order(self) -> int:
        self.order += 1
        return self.order

    # def instruction(self, opcode: str, *args: (enum, str)) -> ElementTree.Element:
    #     instruction = ElementTree.Element("instruction", attrib={"order": str(self.__get_order()), "opcode": opcode})

    def build(self) -> None:
        program = ElementTree.Element("program", attrib={"language": "IPPcode24"})
        # program.append(self.instruction("MOVE", "var", "symb"))
        self.xml = ElementTree.tostring(program, encoding="UTF-8", xml_declaration=True)

    def write(self, file=sys.stdout):
        print(self.xml.decode().replace("'", '"'), file=file)


signal.signal(signal.SIGINT, sigint_handler)
argparser = ArgumentParser(description="Parser for IPPcode24")

args = argparser.parse_args()

parser = IPPcodeParser()
parser.parse()

xml = XMLBuilder()
xml.build()
xml.write()
