"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re


class Parser:
    """Encapsulates access to the input code. Reads an assembly program
    by reading each command line-by-line, parses the current command,
    and provides convenient access to the commands components (fields
    and symbols). In addition, removes all white space and comments.
    """

    def __init__(self, input_file: typing.TextIO) -> None:
        """Opens the input file and gets ready to parse it.

        Args:
            input_file (typing.TextIO): input file.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_file.read().splitlines()
        self.input_lines = input_file.read().splitlines()
        self.last_line_inx = len(self.input_lines) - 1
        self.cur_line = 0
        self.cur_command_line = 0

        while True:
            self.cur_command = re.sub(r'\s+', '', self.input_lines[self.cur_line])
            if self.cur_command == '' or self.cur_command[0] == "/":
                if self.has_more_commands():
                    self.cur_line += 1
            else:
                self.cur_command = self.cur_command.split('//')[0]
                self.last_L_command = True if self.command_type() == "L_COMMAND" else False
                break

    def reset(self) -> None:
        self.cur_line = 0
        self.cur_command_line = 0

        while True:
            self.cur_command = re.sub(r'\s+', '',
                                      self.input_lines[self.cur_line])
            if self.cur_command == '' or self.cur_command[0] == "/":
                if self.has_more_commands():
                    self.cur_line += 1
            else:
                self.cur_command = self.cur_command.split('//')[0]
                self.last_L_command = True if self.command_type() == "L_COMMAND" else False
                break


    def has_more_commands(self) -> bool:
        """Are there more commands in the input?

        Returns:
            bool: True if there are more commands, False otherwise.
        """
        return self.cur_line < self.last_line_inx  # if the file ends with empty/comment lines?

    def advance(self) -> None:
        """Reads the next command from the input and makes it the current command.
        Should be called only if has_more_commands() is true.
        """
        while self.has_more_commands():
            self.cur_line += 1
            self.cur_command = re.sub(r'\s+', '', self.input_lines[self.cur_line])
            if self.cur_command != '' and self.cur_command[0] != "/":
                self.cur_command = self.cur_command.split('//')[0]
                if not self.last_L_command:
                    self.cur_command_line += 1
                self.last_L_command = True if self.command_type() == "L_COMMAND" else False
                break


    def command_type(self) -> str:
        """
        Returns:
            str: the type of the current command:
            "A_COMMAND" for @Xxx where Xxx is either a symbol or a decimal number
            "C_COMMAND" for dest=comp;jump
            "L_COMMAND" (actually, pseudo-command) for (Xxx) where Xxx is a symbol
        """
        if self.cur_command == '' or self.cur_command[0] == "/":
            return None
        if self.cur_command[0] == '@':
            return "A_COMMAND"
        if self.cur_command[0] == '(':
            return "L_COMMAND"
        if self.cur_command != '' and self.cur_command[0] != "/":
            return "C_COMMAND"

    def symbol(self) -> str:
        """
        Returns:
            str: the symbol or decimal Xxx of the current command @Xxx or
            (Xxx). Should be called only when command_type() is "A_COMMAND" or 
            "L_COMMAND".
        """
        return self.cur_command[1:] if self.command_type() == "A_COMMAND" else self.cur_command[1:-1]


    def dest(self) -> str:
        """
        Returns:
            str: the dest mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return (self.cur_command.split('='))[0] if '=' in self.cur_command else ""

    def comp(self) -> str:
        """
        Returns:
            str: the comp mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        comp_jump = self.cur_command.split('=')[1] if '=' in self.cur_command else self.cur_command
        return comp_jump.split(';')[0]

    def jump(self) -> str:
        """
        Returns:
            str: the jump mnemonic in the current C-command. Should be called 
            only when commandType() is "C_COMMAND".
        """
        return self.cur_command.split(';')[1] if ';' in self.cur_command else ""
