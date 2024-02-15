from typing import TextIO
from xml.etree import ElementTree

from modules.instruction import Instruction
from modules.parser import IPPCODE_NAME


class XMLBuilder():

    def __init__(self, indent_width: int = 4) -> None:
        """
        Initialize XMLBuilder with "program" root element
        """
        self.program = ElementTree.Element(
            "program",
            attrib={"language": IPPCODE_NAME}
            )
        self.order = 0
        self.indent_width = indent_width

    def get_instruction_order(self) -> int:
        """"
        Return order of the next instruction
        """
        self.order += 1
        return self.order

    def build_instruction(
            self,
            opcode: str,
            args: list[tuple[str, str]]
            ) -> ElementTree.Element:
        """
        Build a single instruction element
        """
        instruction = ElementTree.Element(
            "instruction",
            attrib={"order": str(self.get_instruction_order()),
                    "opcode": opcode}
            )
        try:
            for i, arg in enumerate(args, start=1):
                ElementTree.SubElement(
                    instruction,
                    f"arg{i}",
                    attrib={"type": arg[0]},
                    ).text = arg[1]
        except TypeError:
            pass
        return instruction

    def build(self, instruction_list: list[Instruction]) -> None:
        """
        Build XML from internal representation
        """
        for instruction in instruction_list:
            self.program.append(
                self.build_instruction(instruction.opcode, instruction.args)
                )

    def write(self, file: TextIO) -> None:
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
