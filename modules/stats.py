##
# @file modules/stats.py
# @author Lukas Tesar <xtesar43@stud.fit.vutbr.cz>
# @brief Module for gathering and printing statistics

import sys
from typing import TextIO

from modules.error import ERR_DESTFILE, ERR_PARAM


class Stats:
    def __init__(self) -> None:
        self.loc = 0
        self.comments = 0
        self.labels = 0
        self.jumps = 0
        self.fwjumps = 0
        self.backjumps = 0
        self.badjumps = 0
        self.opcodes = {}


class UnexpectedArgumentError(Exception):
    pass


class StatsFileUsedTwiceError(Exception):
    pass


class ArgParser:
    def __init__(self, args=None) -> None:
        self.argv = args or sys.argv[1:]
        self.used_files = []

    def print_help(self) -> None:
        if len(self.argv) > 1:
            sys.exit(ERR_PARAM)
        print("Usage: parse.py")
        sys.exit(0)

    def __print_stat(self, stat_name: str, file: TextIO) -> bool:
        if stat_name in [
            "loc", "comments", "labels", "jumps",
            "fwjumps", "backjumps", "badjumps"
        ]:
            file.write(f"{getattr(self.stats, stat_name)}\n")
            return True
        elif stat_name == "frequent":
            if self.stats.opcodes:
                # Sort by frequency
                opcodes_by_freq = sorted(
                    self.stats.opcodes.items(),
                    key=lambda x: x[1],
                    reverse=True)
                # Find the most frequent ones (can be more than one)
                most_freq = max(opcodes_by_freq, key=lambda x: x[1])[1]
                most_freq = [
                            opcode for opcode, _
                            in opcodes_by_freq
                            if _ == most_freq
                ]
                most_freq.sort()
                # The last element cannot contain a comma
                file.write(f"{most_freq[0]}")
                for opcode in most_freq[1:]:
                    file.write(f",{opcode}")
                file.write("\n")
            return True
        else:
            return False

    def __print_stats_group(self) -> None:
        prefix = "--stats="
        if self.argv[0].startswith(prefix):
            file = self.argv[0].removeprefix(prefix)
            if file in self.used_files:
                raise StatsFileUsedTwiceError
            self.used_files.append(file)
            self.argv = self.argv[1:]
            with open(file, "w") as file:
                while self.argv and not self.argv[0].startswith(prefix):
                    argname = self.argv[0].removeprefix("--")
                    if argname.startswith("print="):
                        string = argname.removeprefix("print=")
                        file.write(f"{string}\n")
                    elif argname == "eol":
                        file.write("\n")
                    elif not self.__print_stat(argname, file):
                        raise UnexpectedArgumentError
                    self.argv = self.argv[1:]
        else:
            raise UnexpectedArgumentError

    def handle_help(self) -> None:
        if set(self.argv).intersection(["--help", "-h"]):
            self.print_help()

    def print_stats(self, stats: Stats) -> None:
        self.stats = stats
        while self.argv:
            try:
                self.__print_stats_group()
            except UnexpectedArgumentError:
                sys.exit(ERR_PARAM)
            except StatsFileUsedTwiceError:
                sys.exit(ERR_DESTFILE)
