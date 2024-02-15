#!/usr/bin/env python3.10
# @file parse.py
# @author Lukas Tesar <xtesar43@stud.fit.vutbr.cz>
# @brief Main parser file

import argparse
import signal
import sys

from modules.error import ERR_PARAM, ERR_SIGINT
from modules.parser import IPPcodeParser
from modules.xml import XMLBuilder


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
        return super().print_help(file=sys.stdout)  # print help to stdout


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

    # for instruction in instruction_list:
    #     print(instruction, file=sys.stderr)

    # Build XML from internal representation
    xml = XMLBuilder()
    xml.build(instruction_list)
    xml.write(file=sys.stdout)
