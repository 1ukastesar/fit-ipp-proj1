#!/usr/bin/env python3.10
# @file parse.py
# @author Lukas Tesar <xtesar43@stud.fit.vutbr.cz>
# @brief Main parser file

import signal
import sys

from modules.error import ERR_SIGINT
from modules.parser import IPPcodeParser
from modules.stats import ArgParser
from modules.xml import XMLBuilder


# Handle SIGINT (produced by Ctrl+C and raises KeyboardInterrupt)
# it prints awful traceback everytime
def sigint_handler(signum, frame):
    sys.exit(ERR_SIGINT)


# It can be used as a module or a standalone script
if __name__ == "__main__":

    # Handle KeyboardInterrupt
    signal.signal(signal.SIGINT, sigint_handler)

    argparser = ArgParser()
    argparser.handle_help()

    # Parse input
    parser = IPPcodeParser()
    parser.parse()
    instruction_list = parser.get_internal_repr()

    # Print statistics as requested by provided arguments
    argparser.print_stats(parser.get_stats())

    # Build XML from internal representation
    xml = XMLBuilder()
    xml.build(instruction_list)
    xml.write(file=sys.stdout)
