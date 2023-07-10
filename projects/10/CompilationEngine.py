"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing

TERMINALS = {"keyword",
             "symbol",
             "identifier",
             "integerConstant",
             "stringConstant"
             }

UNARY_OP = {'-', '~', '^', '#'}
OP = {'+', '-', '*', '/', '&', '|', '<', '>', '='}

KEYWORD_CONSTANT = {
    'true', 'false', 'null', 'this'
}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: "JackTokenizer", output_stream) -> None:
        """
        Creates a new compilation engine with the given input and output. The
        next routine called must be compileClass()
        :param input_stream: The input stream.
        :param output_stream: The output stream.
        """
        # Your code goes here!
        # Note that you can write to output_stream like so:
        # output_stream.write("Hello world! \n")
        self.tokenizer = input_stream
        self.output_stream = output_stream

    def compile_class(self) -> None:
        """Compiles a complete class."""
        next_token = self.tokenizer.tell_next_token()
        if next_token != "class":
            raise Exception("jack file should start with class")
        self.output_stream.write("<class>\n")
        self.check_then_write_terminal("keyword", "class")
        self.check_then_write_terminal("identifier")
        self.check_then_write_terminal("symbol", '{')

        next_token = self.tokenizer.tell_next_token()
        while next_token == "static" or next_token == "field":
            self.compile_class_var_dec()
            next_token = self.tokenizer.tell_next_token()

        while next_token == "constructor" or next_token == "function" or next_token == "method":
            self.compile_subroutine()
            next_token = self.tokenizer.tell_next_token()

        self.check_then_write_terminal("symbol", '}')
        self.output_stream.write("</class>\n")

    def check_then_write_type(self):
        next_token = self.tokenizer.tell_next_token()
        if next_token == "int" or next_token == "char" or next_token == "boolean":
            self.check_then_write_terminal("keyword")  # already checked
        else:
            self.check_then_write_terminal("identifier")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        self.output_stream.write("<classVarDec>\n")
        self.check_then_write_terminal("keyword")  # according to prev condition, the token is static or field
        self.check_then_write_type()  # if not 'int' | 'char' | 'boolean' | className (aka identifier) then it raise
        self.check_then_write_terminal("identifier")
        next_token = self.tokenizer.tell_next_token()
        while next_token == ',':
            self.check_then_write_terminal("symbol", ',')
            self.check_then_write_terminal("identifier")
            next_token = self.tokenizer.tell_next_token()
        self.check_then_write_terminal("symbol", ';')
        self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.output_stream.write("<subroutineDec>\n")
        self.check_then_write_terminal("keyword")  # according to prev condition, the token is ('constructor' | 'function' | 'method')
        next_token = self.tokenizer.tell_next_token()
        if next_token == "void":
            self.check_then_write_terminal("keyword")
        else:  # must be type, otherwise raise
            self.check_then_write_type()
        self.check_then_write_terminal("identifier")  # subroutineName
        self.check_then_write_terminal("symbol", '(')
        self.compile_parameter_list()
        self.check_then_write_terminal("symbol", ')')

        # self.compile_subroutine_body()
        self.output_stream.write("<subroutineBody>\n")
        self.check_then_write_terminal("symbol", '{')
        next_token = self.tokenizer.tell_next_token()
        while next_token == "var":
            self.compile_var_dec()
            next_token = self.tokenizer.tell_next_token()
        self.compile_statements()
        self.check_then_write_terminal("symbol", '}')
        self.output_stream.write("</subroutineBody>\n")

        self.output_stream.write("</subroutineDec>\n")


    def compile_parameter_list(self) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        self.output_stream.write("<parameterList>\n")
        next_token = self.tokenizer.tell_next_token()
        if next_token != ')':  # being called only from subroutineDec
            self.check_then_write_type()
            self.check_then_write_terminal("identifier")
            next_token = self.tokenizer.tell_next_token()
            while next_token == ',':
                self.check_then_write_terminal("symbol", ",")
                self.check_then_write_type()
                self.check_then_write_terminal("identifier")
                next_token = self.tokenizer.tell_next_token()
        self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        self.output_stream.write("<varDec>\n")
        self.check_then_write_terminal("keyword")  # var for sure - being called only if next_token is var
        self.check_then_write_type()
        self.check_then_write_terminal("identifier")  # varName
        next_token = self.tokenizer.tell_next_token()
        while next_token == ',':
            self.check_then_write_terminal("symbol", ',')
            self.check_then_write_terminal("identifier")
            next_token = self.tokenizer.tell_next_token()
        self.check_then_write_terminal("symbol", ';')
        self.output_stream.write("</varDec>\n")


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        self.output_stream.write("<statements>\n")  # pass but what if there is no statement?
        next_token = self.tokenizer.tell_next_token()
        while next_token in ["let", "if", "while", "do", "return"]:
            if next_token == "let":
                self.compile_let()
            elif next_token == "if":
                self.compile_if()
            elif next_token == "while":
                self.compile_while()
            elif next_token == "do":
                self.compile_do()
            elif next_token == "return":
                self.compile_return()
            next_token = self.tokenizer.tell_next_token()

        self.output_stream.write("</statements>\n")
        # self.output_stream.write("<statements>\n")
        # while True:
        #     if self.tokenizer.has_more_tokens():
        #         token_type = self.tokenizer.token_type()
        #         if token_type not in ["let", "if", "while", "do", "return"]:
        #             break
        #         self.tokenizer.advance()
        #         if token_type == "keyword":
        #             token = self.tokenizer.get_real_token
        #             if token == "if":
        #                 self.compile_if()
        #             elif token == "while":
        #                 self.compile_while()
        #             elif token == "let":
        #                 self.compile_let()
        #     else:
        #         break
        # self.output_stream.write("</statements>\n")

    def compile_do(self) -> None:
        """Compiles a do statement."""

        self.output_stream.write("<doStatement>\n")
        self.check_then_write_terminal("keyword", "do")  # won't raise. being called only if next is while

        # self.compile_subroutineCall() - pass
        self.check_then_write_terminal("identifier")  # (className | varName) if next condition True, otherwise subroutineName
        next_token = self.tokenizer.tell_next_token()
        if next_token == ".":  # expected: (className |varName) '.' subroutineName '(' expressionList ')'.
            self.check_then_write_terminal("symbol", '.')
            self.check_then_write_terminal("identifier")  # subroutineName
        self.check_then_write_terminal("symbol", '(')  # '(' expressionList ')'
        self.compile_expression_list()
        self.check_then_write_terminal("symbol", ')')

        self.check_then_write_terminal("symbol", ';')
        self.output_stream.write("</doStatement>\n")

    def compile_let(self) -> None:
        """Compiles a let statement."""
        self.output_stream.write("<letStatement>\n")

        self.check_then_write_terminal("keyword", "let")  # wont raise
        self.check_then_write_terminal("identifier")

        next_token = self.tokenizer.tell_next_token()
        if next_token == '[':
            self.check_then_write_terminal("symbol", '[')
            self.compile_expression()
            self.check_then_write_terminal("symbol", ']')

        self.check_then_write_terminal("symbol", '=')
        self.compile_expression()
        self.check_then_write_terminal("symbol", ';')

        self.output_stream.write("</letStatement>\n")

    def check_then_write_terminal(self, expected_terminal_type=None, expected_token=None):
        if expected_terminal_type is None:
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()
                self.write_terminal(self.tokenizer.token_type(), self.tokenizer.get_real_token())
            else:
                raise Exception("end of file")
            return

        if expected_token is None:  # for identifier, integerConstant, stringConstant
            if self.tokenizer.has_more_tokens():
                self.tokenizer.advance()
                if self.tokenizer.token_type() != expected_terminal_type:
                    raise Exception("there supposed to be the terminal type " + expected_terminal_type)
                self.write_terminal(expected_terminal_type, self.tokenizer.get_real_token())
            else:
                raise Exception("end of file")
            return

        if self.tokenizer.has_more_tokens():
            self.tokenizer.advance()
            if self.tokenizer.token_type() != expected_terminal_type or self.tokenizer.get_real_token() != expected_token:
                raise Exception("there supposed to be " + expected_token)
            self.write_terminal(expected_terminal_type, expected_token)
        else:
            raise Exception("end of file")

    def compile_while(self) -> None:
        """Compiles a while statement."""
        self.output_stream.write("<whileStatement>\n")
        self.check_then_write_terminal("keyword", "while")  # won't raise. being called only if next is while

        self.check_then_write_terminal("symbol", '(')
        self.compile_expression()
        self.check_then_write_terminal("symbol", ')')
        self.check_then_write_terminal("symbol", '{')
        self.compile_statements()
        self.check_then_write_terminal("symbol", '}')
        self.output_stream.write("</whileStatement>\n")


    def compile_return(self) -> None:
        """Compiles a return statement."""
        self.output_stream.write("<returnStatement>\n")
        self.check_then_write_terminal("keyword", "return")  # won't raise. being called only if next is return
        next_token = self.tokenizer.tell_next_token()
        if next_token != ';':
            self.compile_expression()
        self.check_then_write_terminal("symbol", ';')
        self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""

        self.output_stream.write("<ifStatement>\n")
        self.check_then_write_terminal("keyword", "if")  # won't raise. being called only if next is while

        self.check_then_write_terminal("symbol", '(')
        self.compile_expression()
        self.check_then_write_terminal("symbol", ')')
        self.check_then_write_terminal("symbol", '{')
        self.compile_statements()
        self.check_then_write_terminal("symbol", '}')

        next_token = self.tokenizer.tell_next_token()
        if next_token == "else":
            self.check_then_write_terminal("keyword", "else")  # won't raise.
            self.check_then_write_terminal("symbol", '{')
            self.compile_statements()
            self.check_then_write_terminal("symbol", '}')

        self.output_stream.write("</ifStatement>\n")

    def write_terminal(self, token_type, token):
        self.output_stream.write("<" + token_type + "> " + token + " </" + token_type + ">\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        self.output_stream.write("<expression>\n")
        self.compile_term()
        next_token = self.tokenizer.tell_next_token()
        while next_token in OP:
            self.check_then_write_terminal("symbol")
            self.compile_term()
            next_token = self.tokenizer.tell_next_token()

        # if self.tokenizer.has_more_tokens():
        #     self.tokenizer.advance()
        #     token_type = self.tokenizer.token_type()
        #     if token_type in TERMINALS:
        #         self.write_terminal(token_type, self.tokenizer.get_real_token())
        # else:
        #     raise Exception("end of file")
        self.output_stream.write("</expression>\n")

    def compile_term(self) -> None:
        """Compiles a term. 
        This routine is faced with a slight difficulty when
        trying to decide between some of the alternative parsing rules.
        Specifically, if the current token is an identifier, the routing must
        distinguish between a variable, an array entry, and a subroutine call.
        A single look-ahead token, which may be one of "[", "(", or "." suffices
        to distinguish between the three possibilities. Any other token is not
        part of this term and should not be advanced over.
        """
        self.output_stream.write("<term>\n")
        next_token = self.tokenizer.tell_next_token()
        if next_token == '(':  # '(' expression ')'
            self.check_then_write_terminal('symbol', '(')
            self.compile_expression()
            self.check_then_write_terminal('symbol', ')')
            self.output_stream.write("</term>\n")
            return
        if next_token in UNARY_OP:  # unaryOp term
            self.check_then_write_terminal('symbol')
            self.compile_term()
            self.output_stream.write("</term>\n")
            return

        if next_token.startswith('"') or next_token[0].isnumeric() or next_token in KEYWORD_CONSTANT:  # integerConstant | stringConstant | keywordConstant
            self.check_then_write_terminal()
            self.output_stream.write("</term>\n")
            return

        # varName | varName '['expression']' | subroutineCall
        # subroutineCall: subroutineName '(' expressionList ')' | (className |
        #                       varName) '.' subroutineName '(' expressionList ')'

        self.check_then_write_terminal("identifier")
        next_token = self.tokenizer.tell_next_token()
        if next_token == '[':  #  varName '['expression']'
            self.check_then_write_terminal("symbol", '[')
            self.compile_expression()
            self.check_then_write_terminal("symbol", ']')
            self.output_stream.write("</term>\n")
            return

        if next_token == ".":  # expected: (className |varName) '.' subroutineName '(' expressionList ')'.
            self.check_then_write_terminal("symbol", '.')
            self.check_then_write_terminal("identifier")  # subroutineName
        next_token = self.tokenizer.tell_next_token()
        if next_token == '(':
            self.check_then_write_terminal("symbol", '(')  # '(' expressionList ')'
            self.compile_expression_list()
            self.check_then_write_terminal("symbol", ')')
        self.output_stream.write("</term>\n")

        # elif next_token == '(' or next_token == '.':  # subroutineCall
        #     next_token = self.tokenizer.tell_next_token()
        #     if next_token == ".":  # expected: (className |varName) '.' subroutineName '(' expressionList ')'.
        #         self.check_then_write_terminal("symbol", '.')
        #         self.check_then_write_terminal("identifier")  # subroutineName
        #     self.check_then_write_terminal("symbol", '(')  # '(' expressionList ')'
        #     self.compile_expression_list()
        #     self.check_then_write_terminal("symbol", ')')
        #
        #
        # if not self.tokenizer.has_more_tokens():
        #     raise Exception("end of file")
        # self.tokenizer.advance()
        # token_type = self.tokenizer.token_type()
        # if token_type in ["integerConstant", "stringConstant", "keyword"]:  # integerConstant | stringConstant | keywordConstant
        #     self.write_terminal(token_type, self.tokenizer.get_real_token())
        #     return
        # if token_type != "identifier":
        #     raise Exception("there should be a term")
        #
        # self.write_terminal("identifier", )
        #
        #
        #
        #
        #     if self.tokenizer.token_type() != expected_terminal_type or self.tokenizer.get_real_token() != expected_token:
        #         raise Exception("there supposed to be " + expected_token)
        #     self.write_terminal(expected_terminal_type, expected_token)
        # else:
        #     raise Exception("end of file")



    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # pass
        self.output_stream.write("<expressionList>\n")
        next_token = self.tokenizer.tell_next_token()
        if next_token != ')':
            self.compile_expression()
            next_token = self.tokenizer.tell_next_token()
            while next_token == ',':
                self.check_then_write_terminal("symbol", ",")
                self.compile_expression()
                next_token = self.tokenizer.tell_next_token()
        self.output_stream.write("</expressionList>\n")

