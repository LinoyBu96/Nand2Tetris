"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""

JUMP = {"": "000", "JGT": "001", "JEQ": "010", "JGE": "011", "JLT": "100",
        "JNE": "101", "JLE": "110", "JMP": "111"}
COMP = {"0": "101010", "1": "111111", "-1": "111010", "D": "001100",
        "A": "110000", "!D": "001101", "!A": "110001", "-D": "001111",
        "-A": "110011", "D+1": "011111", "A+1": "110111", "D-1": "001110",
        "A-1": "110010", "D+A": "000010", "D-A": "010011", "A-D": "000111",
        "D&A": "000000", "D|A": "010101"}
EXTENDED_COMP = {"A<<": "0100000", "D<<": "0110000", "M<<": "1100000", "A>>": "0000000",
                 "D>>": "0010000", "M>>": "1000000"}


class Code:
    """Translates Hack assembly language mnemonics into binary codes."""

    @staticmethod
    def dest(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a dest mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        if mnemonic is None:
            return "000"
        a = "1" if 'A' in mnemonic else "0"
        d = "1" if 'D' in mnemonic else "0"
        m = "1" if 'M' in mnemonic else "0"
        return a + d + m

    @staticmethod
    def comp(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a comp mnemonic string.

        Returns:
            str: the binary code of the given mnemonic.
        """
        if mnemonic in EXTENDED_COMP:
            return "101" + EXTENDED_COMP[mnemonic]
        a = '1' if 'M' in mnemonic else '0'
        mnemonic = mnemonic.replace('M', 'A')
        return "111" + a + COMP[mnemonic]


    @staticmethod
    def jump(mnemonic: str) -> str:
        """
        Args:
            mnemonic (str): a jump mnemonic string.

        Returns:
            str: 3-bit long binary code of the given mnemonic.
        """
        return JUMP[mnemonic]
