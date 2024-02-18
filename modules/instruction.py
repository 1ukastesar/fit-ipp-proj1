##
# @file modules/instruction.py
# @author Lukas Tesar <xtesar43@stud.fit.vutbr.cz>
# @brief Module for parsing and validating instructions

import re
import sys

from modules.error import ERR_OPCODE, ERR_OTHER
from modules.stats import Stats


class InstructionArgumentError(Exception):
    pass


class InstructionBadArgumentCountError(Exception):
    pass


class InstructionPattern:

    var_name = r"([a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*)$"
    __dec = r"^[-+]?[0-9]+$"
    # __dec = r"^[+-]?[0-9]+(?!\S)$"
    __hexa = r"^-?0x[0-9a-fA-F]+$"
    __octal = r"^-?0o?[0-7]+$"
    number = re.compile(r"(" + __dec + r"|" + __hexa + r"|" + __octal + r")")
    label = re.compile(r"^" + var_name)
    const = re.compile(r"^(int|bool|string|nil)@(.*)$")
    var = re.compile(r"^(GF|LF|TF)@" + var_name)
    backslash = re.compile(r"\\")
    escape = re.compile(backslash.pattern + r"[0-9]{3}")
    opcode = re.compile("^[a-zA-Z0-9]+$")


class Instruction:

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
        if (self.pattern.var.match(arg)):
            return "var", arg
        elif (match := self.pattern.const.match(arg)):
            match match.group(1):
                case "nil":
                    if match.group(2) == "nil":
                        return match.group(1), match.group(2)
                case "int":
                    if self.pattern.number.match(match.group(2)):
                        return match.group(1), match.group(2)
                case "bool":
                    if match.group(2).lower() in ["true", "false"]:
                        return match.group(1), match.group(2).lower()
                case "string":
                    string = match.group(2)
                    # For each backslash present
                    for escape in self.pattern.backslash.finditer(string):
                        # Check if it's a valid escape sequence
                        if not self.pattern.escape.match(
                            string[escape.start():]
                        ):
                            raise InstructionArgumentError
                    return match.group(1), match.group(2)
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

    def jump(self, label: str) -> None:
        self.stats.jumps += 1
        if label in self.stats.defined_labels:
            self.stats.backjumps += 1
        else:
            self.stats.unresolved_labels.append(label)

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

        self.stats.jumps += 1

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
        NOT <var> <symb>
        """
        if len(args) != 2:
            raise InstructionBadArgumentCountError

        var = self.var(args[0])
        symb1 = self.symb(args[1])

        return [var, symb1]

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

        label = self.label(args[0])
        if label not in self.stats.defined_labels:
            self.stats.defined_labels.add(label)
            self.stats.labels += 1
            if label in self.stats.unresolved_labels:
                self.stats.fwjumps += \
                    self.stats.unresolved_labels.count(label)
                self.stats.unresolved_labels = list(
                    filter((label).__ne__, self.stats.unresolved_labels)
                )

        return [label]

    def JUMP(self, args: list[str]):
        """
        JUMP <label>
        """
        if len(args) != 1:
            raise InstructionBadArgumentCountError

        label = self.label(args[0])
        self.jump(label)

        return [label]

    def JUMPIFEQ(self, args: list[str]):
        """
        JUMPIFEQ <label> <symb> <symb>
        """
        if len(args) != 3:
            raise InstructionBadArgumentCountError

        label = self.label(args[0])
        symb1 = self.symb(args[1])
        symb2 = self.symb(args[2])
        self.jump(label)

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
        self.jump(label)

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

    def __init__(self, opcode: str, args: list[str], stats: Stats) -> None:
        """
        Try to build an instruction from opcode and arguments
        """
        self.stats = stats
        try:
            if not self.pattern.opcode.match(opcode):
                sys.exit(ERR_OTHER)
            self.args = getattr(self, opcode.upper())(args)
            self.opcode = opcode.upper()
            try:
                self.stats.opcodes[self.opcode] += 1
            except KeyError:
                self.stats.opcodes[self.opcode] = 1
        except AttributeError:
            sys.exit(ERR_OPCODE)
        except (InstructionArgumentError, InstructionBadArgumentCountError):
            sys.exit(ERR_OTHER)

    def __str__(self) -> str:
        return f"{self.opcode} {self.args}"
