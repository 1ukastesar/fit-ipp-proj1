Implementační dokumentace k 1. úloze do IPP 2023/2024
Jméno a příjmení: Lukáš Tesař
Login: xtesar43

# Parser for IPPcode24 - parse.py

## Implementation - core fundamentals

The script uses the most modern and clean Pythonic ways I could find and use to resolve the problem (parsing IPPcode from `stdin` and constructing XML to print on `stdout`).

### `IPPcodeParser` & `XMLBuilder`

I broke the parsing and XML creation logic to two separate classes with their own methods and attributes.

### `Instruction`

In parser, each instruction (line by line) is parsed and constructed separately by implementing some aspects of FSM in the `Instruction` class. On each non-blank line, the class constructor is executed to then call the corresponding method (named after the instruction) and costruct the instruction opcode and argument list, while checking its correctness.

# `XML creation`

Internal representation of the code (basically just a list of `Instruction` objects) is converted to XML by using ElementTree from Python std library list. Upon execution, the main `program` element is built and `instruction` elements are then consequently built and attached one by one on this root element. Lastly, the XML is written to `stdout`, attaching the XML header in the process.

## OOP implementation (NVP extension)

As Python is an OOP language, it's best to code in OOP directly, because almost all Python libraries use it and mixing OOP with non-OOP code is not a good practice, to say the least.

### `ArgumentParser`

Because I wanted to use `argparse` to simplify argument parsing for possible extension addition in the future, I needed to create my own implementation which directly inherits `argparse.ArgumentParser` class, but overwrites two methods for correcting error exit codes and the behavior of `--help`, which, according to the assignment, **must** be exclusive with any other argument (`argparse` simply ignores this problem and prints help whenever `-h` or `--help` is used, even when there are more arguments specified). The use of inheritance and super() to access the ancestor's methods is used here.

### `Exceptions`

For the most cleanest way to end the program, on several points in code I raise an exception instead of just calling `sys.exit`. For that purpose, I inherited base `Exception` class to create two new exceptions for me to use them freely. Then I catch them in the right place in code and I exit the program with correct return code.
