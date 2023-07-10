"""
This file is part of nand2tetris, as taught in The Hebrew University, and
was written by Aviv Yaish. It is an extension to the specifications given
[here](https://www.nand2tetris.org) (Shimon Schocken and Noam Nisan, 2017),
as allowed by the Creative Common Attribution-NonCommercial-ShareAlike 3.0
Unported [License](https://creativecommons.org/licenses/by-nc-sa/3.0/).
"""
STATIC = 'static'
FIELD = 'field'
ARG = 'ARG'
VAR = 'VAR'
TYPE = 0
KIND = 1
INDEX = 2

class SymbolTable:
    """A symbol table that associates names with information needed for Jack
    compilation: type, kind and running index. The symbol table has two nested
    scopes (class/subroutine).
    """

    def __init__(self) -> None:
        """Creates a new empty symbol table."""
        self.class_scope = {}
        self.subroutine_scope = []
        self.counters = {STATIC: 0, FIELD: 0, 'ARG': 0, 'VAR': 0}
        self.n_while = 0
        self.n_if = 0

    def start_subroutine(self) -> None:
        """Starts a new subroutine scope (i.e., resets the subroutine's 
        symbol table).
        """
        self.subroutine_scope.append({})
        self.counters[ARG] = 0
        self.counters[VAR] = 0
        self.n_while = 0
        self.n_if = 0

    def define(self, name: str, type: str, kind: str) -> None:
        """Defines a new identifier of a given name, type and kind and assigns 
        it a running index. "STATIC" and "FIELD" identifiers have a class scope, 
        while "ARG" and "VAR" identifiers have a subroutine scope.

        Args:
            name (str): the name of the new identifier.
            type (str): the type of the new identifier.
            kind (str): the kind of the new identifier, can be:
            "STATIC", "FIELD", "ARG", "VAR".
        """
        if kind == 'LOCAL':
            kind = 'VAR'
        if kind == STATIC:
            self.class_scope[name] = [type, kind, self.counters[STATIC]]
            self.counters[STATIC] += 1
        elif kind == FIELD:
            self.class_scope[name] = [type, kind, self.counters[FIELD]]
            self.counters[FIELD] += 1
        elif kind == ARG:
            self.subroutine_scope[-1][name] = [type, kind, self.counters[ARG]]
            self.counters[ARG] += 1
        elif kind == VAR:
            self.subroutine_scope[-1][name] = [type, kind, self.counters[VAR]]
            self.counters[VAR] += 1

    def var_count(self, kind: str) -> int:
        """
        Args:
            kind (str): can be "STATIC", "FIELD", "ARG", "VAR".

        Returns:
            int: the number of variables of the given kind already defined in 
            the current scope.
        """
        return self.counters[kind]

    def kind_of(self, name: str) -> str:
        """
        Args:
            name (str): name of an identifier.

        Returns:
            str: the kind of the named identifier in the current scope, or None
            if the identifier is unknown in the current scope.
        """
        if name in self.subroutine_scope[-1]:
            kind = self.subroutine_scope[-1][name][KIND]
            if kind == 'VAR':
                kind = 'LOCAL'
        else:
            kind = self.class_scope[name][KIND]
            if kind == 'FIELD':
                kind = 'THIS'
        return kind

    def type_of(self, name: str) -> str:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            str: the type of the named identifier in the current scope.
        """
        if name in self.subroutine_scope[-1]:
            return self.subroutine_scope[-1][name][TYPE]
        return self.class_scope[name][TYPE]


    def index_of(self, name: str) -> int:
        """
        Args:
            name (str):  name of an identifier.

        Returns:
            int: the index assigned to the named identifier.
        """
        if name in self.subroutine_scope[-1]:
            return self.subroutine_scope[-1][name][INDEX]
        return self.class_scope[name][INDEX]

    def get_n_while(self):
        self.n_while += 1
        return self.n_while - 1

    def get_n_if(self):
        self.n_if += 1
        return self.n_if - 1

    def in_cur_or_class_scope(self, name):
        return name in self.class_scope or name in self.subroutine_scope[-1]

    def in_cur_scope(self, name):
        return name in self.subroutine_scope[-1]