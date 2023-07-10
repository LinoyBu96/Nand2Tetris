"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
import typing
from VMWriter import VMWriter
from SymbolTable import SymbolTable
from JackTokenizer import JackTokenizer

TERMINALS = {"keyword",
             "symbol",
             "identifier",
             "integerConstant",
             "stringConstant"
             }

UNARY_OP = {'-', '~', '^', '#'}
OP = {'+', '-', '*', '/', '&', '|', '<', '>', '='}

KEYWORD_CONSTANT = {
    'true': 0, 'false': 0, 'null': 0, 'this': 0
}

class CompilationEngine:
    """Gets input from a JackTokenizer and emits its parsed structure into an
    output stream.
    """

    def __init__(self, input_stream: JackTokenizer, output_stream) -> None:
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
        self.vm_writer = VMWriter(output_stream)
        self.symbol_table = SymbolTable()
        self.class_name = ''
        self.output_stream = None



    def compile_class(self) -> None:
        """Compiles a complete class."""
        next_token = self.tokenizer.tell_next_token()
        if next_token != "class":
            raise Exception("jack file should start with class")
        # self.output_stream.write("<class>\n")
        # self.check_then_write_terminal("keyword", "class")
        self.tokenizer.advance()
        # self.check_then_write_terminal("identifier") == class name
        self.tokenizer.advance()
        self.class_name = self.tokenizer.get_real_token()

        # self.check_then_write_terminal("symbol", '{')
        self.tokenizer.advance()

        next_token = self.tokenizer.tell_next_token()
        while next_token == "static" or next_token == "field":
            self.compile_class_var_dec()
            next_token = self.tokenizer.tell_next_token()

        while next_token == "constructor" or next_token == "function" or next_token == "method":
            self.compile_subroutine()
            next_token = self.tokenizer.tell_next_token()

        # self.check_then_write_terminal("symbol", '}')
        self.tokenizer.advance()
        # self.output_stream.write("</class>\n")

    def check_then_write_type(self):
        next_token = self.tokenizer.tell_next_token()
        if next_token == "int" or next_token == "char" or next_token == "boolean":
            self.check_then_write_terminal("keyword")  # already checked
        else:
            self.check_then_write_terminal("identifier")

    def compile_class_var_dec(self) -> None:
        """Compiles a static declaration or a field declaration."""
        # self.output_stream.write("<classVarDec>\n") == field / static
        self.tokenizer.advance()
        kind = self.tokenizer.get_real_token()
        # self.check_then_write_terminal("keyword")  # according to prev condition, the token is static or field
        self.tokenizer.advance()  # already on var, now advance to kind
        type = self.tokenizer.get_real_token()
        # self.check_then_write_type()  # if not 'int' | 'char' | 'boolean' | className (aka identifier) then it raise
        self.tokenizer.advance()
        name = self.tokenizer.get_real_token()
        self.symbol_table.define(name, type, kind)
        next_token = self.tokenizer.tell_next_token()
        while next_token == ',':
            # self.check_then_write_terminal("symbol", ',')
            self.tokenizer.advance()
            # self.check_then_write_terminal("identifier")
            self.tokenizer.advance()
            name = self.tokenizer.get_real_token()
            self.symbol_table.define(name, type, kind)
            next_token = self.tokenizer.tell_next_token()
        # self.check_then_write_terminal("symbol", ';')
        self.tokenizer.advance()
        # self.output_stream.write("</classVarDec>\n")

    def compile_subroutine(self) -> None:
        """
        Compiles a complete method, function, or constructor.
        You can assume that classes with constructors have at least one field,
        you will understand why this is necessary in project 11.
        """
        self.symbol_table.start_subroutine()
        self.symbol_table.define('this', 'ARG', self.class_name)
        # self.output_stream.write("<subroutineDec>\n")
        # self.check_then_write_terminal("keyword")  # according to prev condition, the token is ('constructor' | 'function' | 'method')
        self.tokenizer.advance()
        fun_type = self.tokenizer.get_real_token()
        # func_type = self.tokenizer.get_real_token() == not interesting
        next_token = self.tokenizer.tell_next_token()
        if next_token == "void":  # edit
            # self.check_then_write_terminal("keyword")  == void
            self.tokenizer.advance()
        else:  # must be type, otherwise raise
            # self.check_then_write_type() == type
            self.tokenizer.advance()
        # self.check_then_write_terminal("identifier")  # subroutineName == func name
        self.tokenizer.advance()
        func_name = self.tokenizer.get_real_token()
        # self.check_then_write_terminal("symbol", '(')
        self.tokenizer.advance()
        self.compile_parameter_list(fun_type)
        # self.check_then_write_terminal("symbol", ')')
        self.tokenizer.advance()

        # """self.compile_subroutine_body()"""
        # self.output_stream.write("<subroutineBody>\n")
        # self.check_then_write_terminal("symbol", '{')
        self.tokenizer.advance()
        next_token = self.tokenizer.tell_next_token()
        while next_token == "var":  # edit! - now it is false, after seven
            self.compile_var_dec()
            next_token = self.tokenizer.tell_next_token()
        n_local = self.symbol_table.var_count('VAR')
        self.vm_writer.write_function(self.class_name + '.' + func_name, n_local)
        self.set_pointer(fun_type)
        self.compile_statements()
        # self.check_then_write_terminal("symbol", '}')
        self.tokenizer.advance()
        # self.output_stream.write("</subroutineBody>\n")

        # self.output_stream.write("</subroutineDec>\n")

    def set_pointer(self, fun_type):
        if fun_type == "method":
            self.vm_writer.write_push('ARG', 0)
            self.vm_writer.write_pop('POINTER', 0)
        if fun_type == 'constructor':
            n_vars = self.symbol_table.var_count('field')
            self.vm_writer.write_push('CONST', n_vars)
            self.vm_writer.write_call('Memory.alloc', 1)
            self.vm_writer.write_pop('POINTER', 0)


    def compile_parameter_list(self, func_name) -> None:
        """Compiles a (possibly empty) parameter list, not including the 
        enclosing "()".
        """
        if func_name == 'method':
            self.symbol_table.define('THIS', 'self', 'ARG')
        # self.output_stream.write("<parameterList>\n")
        next_token = self.tokenizer.tell_next_token()
        kind = 'ARG'
        if next_token != ')':  # being called only from subroutineDec
            # self.check_then_write_type() == arg type
            self.tokenizer.advance()
            type = self.tokenizer.get_real_token()
            # self.check_then_write_terminal("identifier")
            self.tokenizer.advance()
            name = self.tokenizer.get_real_token()
            self.symbol_table.define(name, type, kind)
            next_token = self.tokenizer.tell_next_token()
            while next_token == ',':
                # self.check_then_write_terminal("symbol", ",")
                self.tokenizer.advance()
                # self.check_then_write_type()
                self.tokenizer.advance()
                type = self.tokenizer.get_real_token()
                # self.check_then_write_terminal("identifier")
                self.tokenizer.advance()
                name = self.tokenizer.get_real_token()
                self.symbol_table.define(name, type, kind)
                next_token = self.tokenizer.tell_next_token()
        # self.output_stream.write("</parameterList>\n")

    def compile_var_dec(self) -> None:
        """Compiles a var declaration."""
        # self.output_stream.write("<varDec>\n")
        # self.check_then_write_terminal("keyword")  # var for sure - being called only if next_token is var
        self.tokenizer.advance()
        # self.check_then_write_type() == var type
        self.tokenizer.advance()
        type = self.tokenizer.get_real_token()
        # self.check_then_write_terminal("identifier")  # varName
        self.tokenizer.advance()
        name = self.tokenizer.get_real_token()
        kind = 'LOCAL'
        self.symbol_table.define(name, type, kind)
        next_token = self.tokenizer.tell_next_token()
        while next_token == ',':
            # self.check_then_write_terminal("symbol", ',')
            self.tokenizer.advance()
            # self.check_then_write_terminal("identifier")
            self.tokenizer.advance()
            name = self.tokenizer.get_real_token()
            next_token = self.tokenizer.tell_next_token()
            self.symbol_table.define(name, type, kind)
        # self.check_then_write_terminal("symbol", ';')
        self.tokenizer.advance()
        # self.output_stream.write("</varDec>\n")


    def compile_statements(self) -> None:
        """Compiles a sequence of statements, not including the enclosing 
        "{}".
        """
        # self.output_stream.write("<statements>\n")  # pass but what if there is no statement?
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
        # self.output_stream.write("</statements>\n")

    def push(self, name):
        if name in self.symbol_table.subroutine_scope:
            if self.symbol_table.kind_of(name) == 'VAR':
                self.vm_writer.write_push('local', self.symbol_table.index_of(name))
            elif self.symbol_table.kind_of(name) == 'arg':
                self.vm_writer.write_push('argument', self.symbol_table.index_of(name))
        else:
            if self.symbol_table.kind_of(name) == 'static':
                self.vm_writer.write_push('static', self.symbol_table.index_of(name))
            else:
                self.vm_writer.write_push('THIS', self.symbol_table.index_of(name))

    def compile_do(self) -> None:
        """Compiles a do statement."""
        # self.output_stream.write("<doStatement>\n")
        # self.check_then_write_terminal("keyword", "do")  # won't raise. being called only if next is while
        self.tokenizer.advance()
        n_fun_getters = 0
        # self.compile_subroutineCall() - pass
        # self.check_then_write_terminal("identifier")  # (className | varName) if next condition True, otherwise subroutineName
        self.tokenizer.advance()
        called_fun = self.tokenizer.get_real_token()
        next_token = self.tokenizer.tell_next_token()
        if next_token == ".":  # expected: (className |varName) '.' subroutineName '(' expressionList ')'.
            # self.check_then_write_terminal("symbol", '.')
            self.tokenizer.advance()
            # self.check_then_write_terminal("identifier")  # subroutineName
            self.tokenizer.advance()
            called_fun2 = self.tokenizer.get_real_token()
            if self.symbol_table.in_cur_or_class_scope(called_fun):
                self.vm_writer.write_push(self.symbol_table.kind_of(called_fun), self.symbol_table.index_of(called_fun))
                called_fun = self.symbol_table.type_of(called_fun)
                n_fun_getters += 1
            called_fun = called_fun + '.' + called_fun2
        else:  # calls his own fun
            self.vm_writer.write_push('POINTER', 0)
            n_fun_getters += 1
            called_fun = self.class_name + '.' + called_fun
        # self.check_then_write_terminal("symbol", '(')  # '(' expressionList ')'
        self.tokenizer.advance()
        n_fun_getters += self.compile_expression_list()
        # self.check_then_write_terminal("symbol", ')')
        self.tokenizer.advance()

        # self.check_then_write_terminal("symbol", ';')
        self.tokenizer.advance()
        # self.output_stream.write("</doStatement>\n")
        self.vm_writer.write_call(called_fun, n_fun_getters)
        self.vm_writer.write_pop('TEMP', 0)

    def compile_let(self) -> None:
        """Compiles a let statement."""
        # self.output_stream.write("<letStatement>\n")

        # self.check_then_write_terminal("keyword", "let")  # wont raise
        self.tokenizer.advance()
        # self.check_then_write_terminal("identifier") == name to push into
        self.tokenizer.advance()
        name = self.tokenizer.get_real_token()

        next_token = self.tokenizer.tell_next_token()
        name_of_array = False
        if next_token == '[':  # so identifieris array and we set its element
            name_of_array = True
            # self.check_then_write_terminal("symbol", '[')
            self.tokenizer.advance()
            self.compile_expression()
            # self.check_then_write_terminal("symbol", ']')
            self.tokenizer.advance()
            self.treat_array(name)

        # self.check_then_write_terminal("symbol", '=')
        self.tokenizer.advance()
        self.compile_expression()

        if name_of_array:
            self.vm_writer.write_pop("TEMP", 0)
            self.vm_writer.write_pop("POINTER", 1)
            self.vm_writer.write_push("TEMP", 0)
            self.vm_writer.write_pop("THAT", 0)
        else:
            segment = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            self.vm_writer.write_pop(segment, index)
            # self.output_stream.write("</letStatement>\n")

        # self.check_then_write_terminal("symbol", ';')
        self.tokenizer.advance()

    def treat_array(self, name):
        kind = self.symbol_table.kind_of(name)
        index = self.symbol_table.index_of(name)
        self.vm_writer.write_push(kind, index)
        self.vm_writer.write_arithmetic('+')

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
        # self.output_stream.write("<whileStatement>\n")
        # self.check_then_write_terminal("keyword", "while")  # won't raise. being called only if next is while
        self.tokenizer.advance()
        n_while = self.symbol_table.get_n_while()
        self.vm_writer.write_label('WHILE_EXP' + str(n_while))

        # self.check_then_write_terminal("symbol", '(')
        self.tokenizer.advance()
        self.compile_expression()
        self.vm_writer.write_arithmetic('~') # if expression not true, then jusp after the while
        self.vm_writer.write_if('WHILE_END' + str(n_while))

        # self.check_then_write_terminal("symbol", ')')
        self.tokenizer.advance()
        # self.check_then_write_terminal("symbol", '{')
        self.tokenizer.advance()
        self.compile_statements()

        self.vm_writer.write_goto('WHILE_EXP' + str(n_while))  # return to the loop start
        self.vm_writer.write_label('WHILE_END' + str(n_while))

        # self.check_then_write_terminal("symbol", '}')
        self.tokenizer.advance()
        # self.output_stream.write("</whileStatement>\n")


    def compile_return(self) -> None:
        """Compiles a return statement."""
        # self.output_stream.write("<returnStatement>\n")
        # self.check_then_write_terminal("keyword", "return")  # won't raise. being called only if next is return
        self.tokenizer.advance()
        next_token = self.tokenizer.tell_next_token()
        if next_token != ';':
            self.compile_expression()
        else:
            self.vm_writer.write_push('CONST', 0)
        self.vm_writer.write_return()
        # self.check_then_write_terminal("symbol", ';')
        self.tokenizer.advance()
        # self.output_stream.write("</returnStatement>\n")

    def compile_if(self) -> None:
        """Compiles a if statement, possibly with a trailing else clause."""

        # self.output_stream.write("<ifStatement>\n")
        # self.check_then_write_terminal("keyword", "if")  # won't raise. being called only if next is while
        self.tokenizer.advance()
        # self.check_then_write_terminal("symbol", '(')
        self.tokenizer.advance()
        self.compile_expression()
        # self.check_then_write_terminal("symbol", ')')
        self.tokenizer.advance()

        n_if = self.symbol_table.get_n_if()
        self.vm_writer.write_if('IF_TRUE' + str(n_if))
        self.vm_writer.write_goto('IF_FALSE' + str(n_if))
        self.vm_writer.write_label('IF_TRUE' + str(n_if))

        # self.check_then_write_terminal("symbol", '{')
        self.tokenizer.advance()
        self.compile_statements()
        # self.check_then_write_terminal("symbol", '}')
        self.tokenizer.advance()

        next_token = self.tokenizer.tell_next_token()
        if next_token == "else":
            # self.check_then_write_terminal("keyword", "else")  # won't raise.
            self.tokenizer.advance()
            # self.check_then_write_terminal("symbol", '{')
            self.tokenizer.advance()

            self.vm_writer.write_goto('IF_END' + str(n_if))
            self.vm_writer.write_label('IF_FALSE' + str(n_if))
            self.compile_statements()
            # self.check_then_write_terminal("symbol", '}')
            self.tokenizer.advance()
            self.vm_writer.write_label('IF_END' + str(n_if))
        else:
            self.vm_writer.write_label('IF_FALSE' + str(n_if))

        # self.output_stream.write("</ifStatement>\n")

    def write_terminal(self, token_type, token):
        self.output_stream.write("<" + token_type + "> " + token + " </" + token_type + ">\n")

    def compile_expression(self) -> None:
        """Compiles an expression."""
        # self.output_stream.write("<expression>\n")
        self.compile_term()
        next_token = self.tokenizer.tell_next_token()
        operators = []
        while next_token in OP:
            # self.check_then_write_terminal("symbol")
            self.tokenizer.advance()
            op = (self.tokenizer.get_real_token()).upper()  # return a val from TOKEN_TYPES in tokenizer
            self.compile_term()
            self.vm_writer.write_arithmetic(op, is_binary=True)
            next_token = self.tokenizer.tell_next_token()
        # for op in operators:
        #     pass
        # self.output_stream.write("</expression>\n")

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
        name_of_array = False
        # self.output_stream.write("<term>\n")
        next_token = self.tokenizer.tell_next_token()
        if next_token == '(':  # '(' expression ')'
            # self.check_then_write_terminal('symbol', '(')
            self.tokenizer.advance()
            self.compile_expression()
            # self.check_then_write_terminal('symbol', ')')
            self.tokenizer.advance()
            # self.output_stream.write("</term>\n")
            return
        if next_token in UNARY_OP:  # unaryOp term
            # self.check_then_write_terminal('symbol')
            self.tokenizer.advance()
            unary_op = self.tokenizer.get_real_token()
            self.compile_term()
            self.vm_writer.write_arithmetic(unary_op)
            # self.output_stream.write("</term>\n")
            return

        if next_token[0].isnumeric():  # integerConstant
            # self.check_then_write_terminal()
            self.tokenizer.advance()
            index = self.tokenizer.get_real_token()
            self.vm_writer.write_push('CONST', index)
            # self.output_stream.write("</term>\n")
            return
        elif next_token in KEYWORD_CONSTANT:  # keywordConstant
            # self.check_then_write_terminal()
            self.tokenizer.advance()
            index = self.tokenizer.get_real_token()
            temp = index
            index = KEYWORD_CONSTANT[index]
            if temp == 'this':
                self.vm_writer.write_push('POINTER', index)
                return
            self.vm_writer.write_push('CONST', index)
            if temp == 'true':
                self.vm_writer.write_arithmetic('~')
            # self.output_stream.write("</term>\n")
            return
        # elif next_token in KEYWORD_CONSTANT:  # keywordConstant - bothhhhhhhhhhhhh
        #     # self.check_then_write_terminal()
        #     self.tokenizer.advance()
        #     index = self.tokenizer.get_real_token()
        #     temp = index
        #     if index in KEYWORD_CONSTANT:
        #         index = KEYWORD_CONSTANT[index]
        #     self.vm_writer.write_push('CONST', index)
        #     if temp == 'true':
        #         self.vm_writer.write_arithmetic('~')
        #     # self.output_stream.write("</term>\n")
        #     return
        elif next_token.startswith('"'):  # edit - strings in our program??
            # self.check_then_write_terminal()
            self.tokenizer.advance()
            text = self.tokenizer.get_real_token()
            self.vm_writer.write_push('CONST', len(text))
            self.vm_writer.write_call('String.new', 1)
            for char in text:
                self.vm_writer.write_push('CONST', ord(char))
                self.vm_writer.write_call('String.appendChar', 2)
            # self.output_stream.write("</term>\n")
            return

        # varName | varName '['expression']' | subroutineCall
        # subroutineCall: subroutineName '(' expressionList ')' | (className |
        #                       varName) '.' subroutineName '(' expressionList ')'

        # self.check_then_write_terminal("identifier")
        self.tokenizer.advance()
        name = self.tokenizer.get_real_token()
        next_token = self.tokenizer.tell_next_token()
        if next_token == '[':  #  varName '['expression']'  - edit not in convertToBin
            name_of_array = True
            # self.check_then_write_terminal("symbol", '[')
            self.tokenizer.advance()
            self.compile_expression()
            # self.check_then_write_terminal("symbol", ']')
            self.tokenizer.advance()
            # self.output_stream.write("</term>\n")
            self.treat_array(name)
            # return

        n_local = 0
        if next_token == ".":  # expected: (className |varName) '.' subroutineName '(' expressionList ')'.
            # self.check_then_write_terminal("symbol", '.')
            self.tokenizer.advance()
            # self.check_then_write_terminal("identifier")  # subroutineName
            self.tokenizer.advance()
            # name = name + '.' + self.tokenizer.get_real_token()
            second_name = self.tokenizer.get_real_token()
            # if self.tokenizer.get_real_token() =='move' and name.split('.')[0] == 'ball':
            if self.symbol_table.in_cur_or_class_scope(name):
                self.vm_writer.write_push(self.symbol_table.kind_of(name), self.symbol_table.index_of(name))
                n_local += 1
                name = self.symbol_table.type_of(name) + '.' + second_name
            else:

                name = name + '.' + second_name
        next_token = self.tokenizer.tell_next_token()
        if next_token == '(':
            # self.check_then_write_terminal("symbol", '(')  # '(' expressionList ')'
            self.tokenizer.advance()
            n_local += self.compile_expression_list()
            # self.check_then_write_terminal("symbol", ')')
            self.tokenizer.advance()
            self.vm_writer.write_call(name, n_local)
        else:  #var, y in: let x = y
            if name_of_array:
                self.vm_writer.write_pop('POINTER', 1)
                self.vm_writer.write_push('THAT', 0)
                return
            segment = self.symbol_table.kind_of(name)
            index = self.symbol_table.index_of(name)
            self.vm_writer.write_push(segment, index)


    def compile_expression_list(self) -> None:
        """Compiles a (possibly empty) comma-separated list of expressions."""
        # self.output_stream.write("<expressionList>\n")
        list_size = 0
        next_token = self.tokenizer.tell_next_token()
        if next_token != ')':  # function that is being called gets some args
            self.compile_expression()
            next_token = self.tokenizer.tell_next_token()
            list_size += 1
            while next_token == ',':  # function that is being called gets several args
                # self.check_then_write_terminal("symbol", ",")
                self.tokenizer.advance()
                self.compile_expression()
                next_token = self.tokenizer.tell_next_token()
                list_size += 1
        return list_size
        # self.output_stream.write("</expressionList>\n")

