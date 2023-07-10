"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
import re

TOKEN_TYPES = {
    "KEYWORD": "keyword",
    "SYMBOL": "symbol",
    "IDENTIFIER": "identifier",
    "INT_CONST": "integerConstant",
    "STRING_CONST": "stringConstant"
}

KEYWORDS = {
    "class", "constructor", "function", "method", "field", "static", "var", "int", "char", "boolean", "void",
    "true", "false", "null", "this", "let", "do", "if", "else", "while", "return"
}

SYMBOLS = {'{', '}', '(', ')', '[', ']', '.', ',', ';', '+', '-', '*', '/', '&', '|', '<', '>', '=', '~', '^', '#'}
SPECIAL_SYMBOLS = {'<': '&lt;', '>': '&gt;', '&': '&amp;'}



class JackTokenizer:
    """Removes all comments from the input stream and breaks it
    into Jack language tokens, as specified by the Jack grammar.

    # Jack Language Grammar

    A Jack file is a stream of characters. If the file represents a
    valid program, it can be tokenized into a stream of valid tokens. The
    tokens may be separated by an arbitrary number of whitespace characters,
    and comments, which are ignored. There are three possible comment formats:
    /* comment until closing */ , /** API comment until closing */ , and
    // comment until the line’s end.

    - ‘xxx’: quotes are used for tokens that appear verbatim (‘terminals’).
    - xxx: regular typeface is used for names of language constructs
           (‘non-terminals’).
    - (): parentheses are used for grouping of language constructs.
    - x | y: indicates that either x or y can appear.
    - x?: indicates that x appears 0 or 1 times.
    - x*: indicates that x appears 0 or more times.

    ## Lexical Elements

    The Jack language includes five types of terminal elements (tokens).

    - keyword: 'class' | 'constructor' | 'function' | 'method' | 'field' |
               'static' | 'var' | 'int' | 'char' | 'boolean' | 'void' | 'true' |
               'false' | 'null' | 'this' | 'let' | 'do' | 'if' | 'else' |
               'while' | 'return'
    - symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
    - integerConstant: A decimal number in the range 0-32767.
    - StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
    - identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.

    ## Program Structure

    A Jack program is a collection of classes, each appearing in a separate
    file. A compilation unit is a single class. A class is a sequence of tokens
    structured according to the following context free syntax:

    - class: 'class' className '{' classVarDec* subroutineDec* '}'
    - classVarDec: ('static' | 'field') type varName (',' varName)* ';'
    - type: 'int' | 'char' | 'boolean' | className
    - subroutineDec: ('constructor' | 'function' | 'method') ('void' | type) subroutineName '(' parameterList ')' subroutineBody
    - parameterList: ((type varName) (',' type varName)*)?
    - subroutineBody: '{' varDec* statements '}'
    - varDec: 'var' type varName (',' varName)* ';'
    - className: identifier
    - subroutineName: identifier
    - varName: identifier

    ## Statements

    - statements: statement*
    - statement: letStatement | ifStatement | whileStatement | doStatement |
                 returnStatement
    - letStatement: 'let' varName ('[' expression ']')? '=' expression ';'
    - ifStatement: 'if' '(' expression ')' '{' statements '}' ('else' '{'
                   statements '}')?
    - whileStatement: 'while' '(' 'expression' ')' '{' statements '}'
    - doStatement: 'do' subroutineCall ';'
    - returnStatement: 'return' expression? ';'

    ## Expressions

    - expression: term (op term)*
    - term: integerConstant | stringConstant | keywordConstant | varName |
            varName '['expression']' | subroutineCall | '(' expression ')' |
            unaryOp term
    - subroutineCall: subroutineName '(' expressionList ')' | (className |
                      varName) '.' subroutineName '(' expressionList ')'
    - expressionList: (expression (',' expression)* )?
    - op: '+' | '-' | '*' | '/' | '&' | '|' | '<' | '>' | '='
    - unaryOp: '-' | '~' | '^' | '#'
    - keywordConstant: 'true' | 'false' | 'null' | 'this'

    Note that ^, # correspond to shiftleft and shiftright, respectively.
    """

    def __init__(self, input_stream: typing.TextIO) -> None:
        """Opens the input stream and gets ready to tokenize it.

        Args:
            input_stream (typing.TextIO): input stream.
        """
        # Your code goes here!
        # A good place to start is to read all the lines of the input:
        # input_lines = input_stream.read().splitlines()
        self.input_lines = input_stream.read().splitlines()
        self.cur_line_tokens = None
        self.cur_token = None
        self._has_more_tokens = True
        self._cur_token_type = None
        self._real_cur_token = None
        self.set_next_line_tokens()

        # self.cur_line_index = 0
        # self.cur_line = self.input_lines[self.cur_line_index]
        # self.pointer_inline = 0
        # self.lenght_line = len(self.cur_line)

    def get_real_token(self):
        return self._real_cur_token

    def tell_next_token(self):
        return self.cur_line_tokens[0]

    def drop_comments(self, line):
        line = line.split('//')[0]  # removes inline comment
        # if '/' in current_line:
        #     current_line.split()
        line = re.sub("/\*.*?\*/", "", line)  # removes /* ...*/
        # remove comments over multilines
        line = line.split('//')[0]
        return line

    def is_multiline_comment(self, line):
        return len(line.split('/*')) > 1

    def multiline_comment_ends(self, line):
        return len(line.split('*/')) > 1

    def set_next_line_tokens(self):
        """
        is called only if self.cur_line_arr = [] / None
        """
        cur_line = ""
        is_multiline_comment = False
        while not cur_line.strip() or is_multiline_comment:
            if not self.input_lines:
                self._has_more_tokens = False
                return
            cur_line = self.drop_comments(self.input_lines.pop(0))
            if is_multiline_comment:
                if self.multiline_comment_ends(cur_line):
                    is_multiline_comment = False
                    cur_line = ""
                continue
            is_multiline_comment = self.is_multiline_comment(cur_line)

        # pattern = r'(\{|\}|\(|\)|\[|\]|\.|,|;|\+|=|\*|/|&|\||<|>|=|~|\d+|".*?"|[\w_]+)'
        # pattern = r'(\{|\}|\(|\)|\[|\]|\.|,|;|\+|=|\*|/|&|\||<|>|=|~|\d+|".*?"|class|constructor|function|method|field|' \
        #           r'static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return|[\w_]+)'
        pattern = r'(\{|\}|\(|\)|\[|\]|\.|,|;|\+|-|\*|/|&|\||<|>|=|~|\^|#|\d+|".*?"|class|constructor|function|method|field|' \
                  r'static|var|int|char|boolean|void|true|false|null|this|let|do|if|else|while|return|[\w_]+)'
        self.cur_line_tokens = re.findall(pattern, cur_line)

    def has_more_tokens(self) -> bool:
        """Do we have more tokens in the input?

        Returns:
            bool: True if there are more tokens, False otherwise.
        """
        return self._has_more_tokens

    # def advance_to_next_line(self):
    #     self.cur_line_index += 1
    #     self.cur_line = self.input_lines[self.cur_line_index]
    #     self.pointer_inline = 0
    #     self.lenght_line = len(self.cur_line)
    #
    # def is_inline_comment(self):


    def advance(self) -> None:
        """Gets the next token from the input and makes it the current token.
        This method should be called if has_more_tokens() is true.
        Initially there is no current token.
        """
        if not self._has_more_tokens:
            raise Exception("JackTokenizer.advance should be called if has_more_tokens() is true")
        self.cur_token = self.cur_line_tokens.pop(0)
        self._cur_token_type = None
        if not self.cur_line_tokens:  # in case everything was popped and no tokens left
            self.set_next_line_tokens()
        # pattern = r'(\{|\}|\(|\)|\[|\]|\.|,|;|\+|=|\*|/|&|\||<|>|=|~|\d+|".*?"|\S+)'

        # while self.cur_line[self.pointer_inline] == ' ':
        #     self.pointer_inline += 1
        #     if self.pointer_inline == self.lenght_line:
        #         self.advance_to_next_line()
        #
        #
        #
        # self.cur_line_index += 1
        # while self.input_lines[self.cur_line_index].startswith('/'):
        #     if self.input_lines[self.cur_line_index].startswith('//'): # means it is an in-line comment only
        #         self.cur_line_index += 1
        #         continue

    def token_type(self) -> str:
        """
        Returns:
            str: the type of the current token, can be
            "KEYWORD", "SYMBOL", "IDENTIFIER", "INT_CONST", "STRING_CONST"
        """
        if self.cur_token in KEYWORDS:
            self._cur_token_type = "KEYWORD"
            self._real_cur_token = self.keyword()
        elif self.cur_token in SYMBOLS:
            self._cur_token_type = "SYMBOL"
            self._real_cur_token = self.symbol()
        elif self.cur_token.isdecimal():
            self._cur_token_type = "INT_CONST"
            self._real_cur_token = self.int_val()
        elif self.cur_token.startswith('"') and self.cur_token.endswith('"'):
            self._cur_token_type = "STRING_CONST"
            self._real_cur_token = self.string_val()
        else:
            self._cur_token_type = "IDENTIFIER"  # dont deal with a:a = 5
            self._real_cur_token = self.identifier()
        return TOKEN_TYPES[self._cur_token_type]

    def keyword(self) -> str:
        """
        Returns:
            str: the keyword which is the current token.
            Should be called only when token_type() is "KEYWORD".
            Can return "CLASS", "METHOD", "FUNCTION", "CONSTRUCTOR", "INT",
            "BOOLEAN", "CHAR", "VOID", "VAR", "STATIC", "FIELD", "LET", "DO",
            "IF", "ELSE", "WHILE", "RETURN", "TRUE", "FALSE", "NULL", "THIS"
        """
        if self._cur_token_type != "KEYWORD":
            raise Exception('JackTokenizer.keyword Should be called only after token_type() is being called and  its valye "KEYWORD".')
        return self.cur_token

    def symbol(self) -> str:
        """
        Returns:
            str: the character which is the current token.
            Should be called only when token_type() is "SYMBOL".
            Recall that symbol was defined in the grammar like so:
            symbol: '{' | '}' | '(' | ')' | '[' | ']' | '.' | ',' | ';' | '+' |
              '-' | '*' | '/' | '&' | '|' | '<' | '>' | '=' | '~' | '^' | '#'
        """
        if self._cur_token_type != "SYMBOL":
            raise Exception('JackTokenizer.keyword Should be called only after token_type() is being called and  its valye "SYMBOL".')
        if self.cur_token in SPECIAL_SYMBOLS:
            return SPECIAL_SYMBOLS[self.cur_token]
        return self.cur_token

    def identifier(self) -> str:
        """
        Returns:
            str: the identifier which is the current token.
            Should be called only when token_type() is "IDENTIFIER".
            Recall that identifiers were defined in the grammar like so:
            identifier: A sequence of letters, digits, and underscore ('_') not
                  starting with a digit. You can assume keywords cannot be
                  identifiers, so 'self' cannot be an identifier, etc'.
        """
        if self._cur_token_type != "IDENTIFIER":
            raise Exception('JackTokenizer.keyword Should be called only after token_type() is being called and  its valye "IDENTIFIER".')
        return self.cur_token

    def int_val(self) -> int:
        """
        Returns:
            str: the integer value of the current token.
            Should be called only when token_type() is "INT_CONST".
            Recall that integerConstant was defined in the grammar like so:
            integerConstant: A decimal number in the range 0-32767.
        """
        if self._cur_token_type != "INT_CONST":
            raise Exception('JackTokenizer.keyword Should be called only after token_type() is being called and  its valye "INT_CONST".')
        return self.cur_token

    def string_val(self) -> str:
        """
        Returns:
            str: the string value of the current token, without the double
            quotes. Should be called only when token_type() is "STRING_CONST".
            Recall that StringConstant was defined in the grammar like so:
            StringConstant: '"' A sequence of Unicode characters not including
                      double quote or newline '"'
        """
        if self._cur_token_type != "STRING_CONST":
            raise Exception('JackTokenizer.keyword Should be called only after token_type() is being called and  its valye "STRING_CONST".')
        return self.cur_token[1:-1]