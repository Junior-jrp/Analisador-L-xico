from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Token:
    tipo: str
    lexema: str
    atributo: object = None

    def __str__(self) -> str:
        if self.atributo is not None:
            return f"Token({self.tipo}, {self.lexema!r}, attr={self.atributo!r})"
        return f"Token({self.tipo}, {self.lexema!r})"


KEYWORDS: frozenset[str] = frozenset({
    "auto",     "break",    "case",     "char",     "const",    "continue",
    "default",  "do",       "double",   "else",     "enum",     "extern",
    "float",    "for",      "goto",     "if",       "int",      "long",
    "register", "return",   "short",    "signed",   "sizeof",   "static",
    "struct",   "switch",   "typedef",  "union",    "unsigned", "void",
    "volatile", "while",
})

COMPOUND_OPERATORS: tuple[str, ...] = (
    "...",
    "->",
    "==", "!=", "<=", ">=",
    "&&", "||",
    "+=", "-=", "*=", "/=", "%=", "&=", "|=", "^=",
    "<<", ">>",
    "++", "--",
)

SINGLE_OPERATORS: frozenset[str] = frozenset("+-*/%=<>!&|^~;,.(){}[]?")

TOKEN_TYPES: dict[str, str] = {
    "KEYWORD"       : "KEYWORD",
    "IDENTIFIER"    : "IDENTIFIER",
    "INT_LITERAL"   : "INT_LITERAL",
    "FLOAT_LITERAL" : "FLOAT_LITERAL",
    "CHAR_LITERAL"  : "CHAR_LITERAL",
    "STRING_LITERAL": "STRING_LITERAL",
    "OPERATOR"      : "OPERATOR",
    "DELIMITER"     : "DELIMITER",
    "PP_DIRECTIVE"  : "PP_DIRECTIVE",
    "EOF"           : "EOF",
    "ERROR"         : "ERROR",
}

DELIMITER_CHARS: frozenset[str] = frozenset(";,(){}[]")