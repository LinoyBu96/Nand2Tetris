"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

ARITMETHICS_COMMANDS = {"add", "sub", "and", "or", "eq", "gt", "lt", "neg", "not", "shiftleft", "shiftright"}

class Parser:
    """
    # Parser

    Handles the parsing of a single .vm file, and encapsulates access to the
    input code. It reads VM commands, parses them, and provides convenient
    access to their components.
    In addition, it removes all white space and comments.

    ## VM Language Specification

    A .vm file is a stream of characters. If the file represents a
    valid program, it can be translated into a stream of valid assembly
    commands. VM commands may be separated by an arbitrary number of whitespace
    characters and comments, which are ignored. Comments begin with "//" and
    last until the line’s end.
    The different parts of each VM command may also be separated by an arbitrary
    number of non-newline whitespace characters.

    - Arithmetic commands:
      - add, sub, and, or, eq, gt, lt
      - neg, not, shiftleft, shiftright
    - Memory segment manipulation:
      - push <segment> <number>
      - pop <segment that is not constant> <number>
      - <segment> can be any of: argument, local, static, constant, this, that,
                                 pointer, temp
    - Branching (only relevant for project 8):
      - label <label-name>
      - if-goto <label-name>
      - goto <label-name>
      - <label-name> can be any combination of non-whitespace characters.
    - Functions (only relevant for project 8):
      - call <function-name> <n-args>
      - function <function-name> <n-vars>
      - return
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Gets ready to parse the input file.

        Args:
            input_file (typing.TextIO): input file.
        """
        self.input_lines = input_file.read().splitlines()
        self.last_line_inx = len(self.input_lines) - 1
        self.cur_line = 0
        while True:
            self.cur_command = self.input_lines[self.cur_line]
            if self.cur_command == '' or self.cur_command[0] == "/":
                if self.has_more_commands():
                    self.cur_line += 1
            else:
                self.cur_command = self.cur_command.split('//')[0]
                break

    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_line < self.last_line_inx  # if the file ends with empty/comment lines?


    def advance(self) -> None:
        """Reads the next command from the input and makes it the current
        command. Should be called only if has_more_commands() is true. Initially
        there is no current command.
        """
        while self.has_more_commands():
            self.cur_line += 1
            self.cur_command = self.input_lines[self.cur_line]
            if self.cur_command != '' and self.cur_command[0] != "/":
                self.cur_command = self.cur_command.split('//')[0]
                break

    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current VM command.
            "C_ARITHMETIC" is returned for all arithmetic commands.
            For other commands, can return:
            "C_PUSH", "C_POP", "C_LABEL", "C_GOTO", "C_IF", "C_FUNCTION",
            "C_RETURN", "C_CALL".
        """
        command_type = self.cur_command.split(" ")[0]
        if command_type in ARITMETHICS_COMMANDS:
            return "C_ARITHMETIC"
        if command_type == 'push':
            return "C_PUSH"
        if command_type == 'pop':
            return "C_POP"
        if command_type == 'label':
            return "C_LABEL"
        if command_type == 'goto':
            return "C_GOTO"
        if command_type == 'if-goto':
            return "C_IF"
        if command_type == 'function':
            return "C_FUNCTION"
        if command_type == 'return':
            return "C_RETURN"
        if command_type == 'call':
            return "C_CALL"


    def arg1(self) -> str:
        """
        Returns:
            str: the first argument of the current command. In case of
            "C_ARITHMETIC", the command itself (add, sub, etc.) is returned.
            Should not be called if the current command is "C_RETURN".
        """
        cur_command_type = self.command_type()
        if cur_command_type == "C_RETURN":
            return
        if cur_command_type == "C_ARITHMETIC":
            return self.cur_command
        return self.cur_command.split(" ")[1]

    def arg2(self) -> int:
        """
        Returns:
            int: the second argument of the current command. Should be
            called only if the current command is "C_PUSH", "C_POP",
            "C_FUNCTION" or "C_CALL".
        """
        cur_command_type = self.command_type()
        if cur_command_type == "C_PUSH" or cur_command_type == "C_POP" or\
                cur_command_type == "C_FUNCTION" or cur_command_type == "C_CALL":
            return int(self.cur_command.split(" ")[2])
