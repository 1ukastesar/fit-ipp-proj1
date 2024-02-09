#!/usr/bin/env python3.10

import argparse
import sys

from xml.etree import ElementTree

ERR_PARAM    = 10
ERR_HEADER   = 21
ERR_OPCODE   = 22
ERR_OTHER    = 23
ERR_INTERNAL = 99


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        """
        Override default error handler to change argparse exit code
        """

        self.print_usage(sys.stderr)
        self.exit(ERR_PARAM, '%s: error: %s\n' % (self.prog, message))

    def print_help(self, file=None):
        """
        Override default help handler to make --help exclusive with other arguments
        """

        if len(sys.argv) > 2:
            self.error("--help can't be combined with other arguments")
        return super().print_help(file)


class IPPcodeParser():

    def validate(self, file=sys.stdin):
        file.readline()
        pass


class XMLBuilder():

    def __init__(self):
        self.xml = ""

    def build(self):
        root = ElementTree.Element("program", attrib={"language": "IPPcode24"})
        self.xml = ElementTree.tostring(root, encoding="UTF-8", xml_declaration=True)

    def write(self, file=sys.stdout):
        print(self.xml.decode().replace("'", '"'), file=file)


argparser = ArgumentParser(description="Parser for IPPcode24")

args = argparser.parse_args()

parser = IPPcodeParser()
parser.validate()

writer = XMLBuilder()
writer.build()
writer.write()
