"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import os
import sys
import typing
from CompilationEngine import CompilationEngine
from JackTokenizer import JackTokenizer

def tokanizer_test(tokenizer: JackTokenizer, output_file: typing.TextIO):
    output_file.write("<tokens>\n")
    while tokenizer.has_more_tokens():
        tokenizer.advance()
        token_classification = tokenizer.token_type()
        output_file.write("<" + token_classification + ">" + tokenizer.get_real_token() + "</" + token_classification + ">\n")

    output_file.write("</tokens>")

def analyze_file(
        input_file: typing.TextIO, output_file: typing.TextIO) -> None:
    """Analyzes a single file.

    Args:
        input_file (typing.TextIO): the file to analyze.
        output_file (typing.TextIO): writes all output to this file.
    """
    tokenizer = JackTokenizer(input_file)
    #tokanizer_test(tokenizer, output_file)
    engine = CompilationEngine(tokenizer, output_file)
    engine.compile_class()
    # engine.output_stream.write("<class>\n")
    # while engine.tokenizer.has_more_tokens():
    #     engine.tokenizer.advance()
    #     token_classification = engine.tokenizer.token_type()
    #     if
    #     # output_file.write(
    #     #     "<" + token_classification + ">" + engine.tokenizer.get_real_token() + "</" + token_classification + ">\n")
    # engine.output_stream.write("</class>")



if "__main__" == __name__:
    # Parses the input path and calls analyze_file on each input file.
    # This opens both the input and the output files!
    # Both are closed automatically when the code finishes running.
    # If the output file does not exist, it is created automatically in the
    # correct path, using the correct filename.
    if not len(sys.argv) == 2:
        sys.exit("Invalid usage, please use: JackAnalyzer <input path>")
    argument_path = os.path.abspath(sys.argv[1])
    if os.path.isdir(argument_path):
        files_to_assemble = [
            os.path.join(argument_path, filename)
            for filename in os.listdir(argument_path)]
    else:
        files_to_assemble = [argument_path]
    for input_path in files_to_assemble:
        filename, extension = os.path.splitext(input_path)
        if extension.lower() != ".jack":
            continue
        output_path = filename + ".xml"
        with open(input_path, 'r') as input_file, \
                open(output_path, 'w') as output_file:
            analyze_file(input_file, output_file)