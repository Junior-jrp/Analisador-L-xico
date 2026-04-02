from __future__ import annotations

from token_types import (
    Token,
    KEYWORDS,
    COMPOUND_OPERATORS,
    SINGLE_OPERATORS,
    TOKEN_TYPES,
    DELIMITER_CHARS,
)


class Lexer:
    def __init__(self, source: str) -> None:
        self.source: str                  = source
        self.pos: int                     = 0
        self.line: int                    = 1
        self.col: int                     = 1
        self.tokens: list[Token]          = []
        self.symbol_table: dict[str, int] = {}
        self.errors: list[str]            = []

    def _current(self) -> str:
        return self.source[self.pos] if self.pos < len(self.source) else ""

    def _peek(self, offset: int = 1) -> str:
        idx = self.pos + offset
        return self.source[idx] if idx < len(self.source) else ""

    def _advance(self) -> str:
        ch = self._current()
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def _skip_whitespace(self) -> None:
        while self._current() in (" ", "\t", "\r", "\n"):
            self._advance()

    def _skip_line_comment(self) -> None:
        while self._current() and self._current() != "\n":
            self._advance()

    def _skip_block_comment(self) -> None:
        start_line = self.line
        self._advance()
        self._advance()
        while self._current():
            if self._current() == "*" and self._peek() == "/":
                self._advance()
                self._advance()
                return
            self._advance()
        msg = f"[Linha {start_line}] Comentário de bloco não fechado."
        self.errors.append(msg)
        self.tokens.append(Token(TOKEN_TYPES["ERROR"], "/*", msg))

    def _read_identifier_or_keyword(self) -> Token:
        chars: list[str] = []
        while self._current() and (self._current().isalnum() or self._current() == "_"):
            chars.append(self._advance())
        lexeme = "".join(chars)
        if lexeme in KEYWORDS:
            return Token(TOKEN_TYPES["KEYWORD"], lexeme)
        self.symbol_table[lexeme] = self.symbol_table.get(lexeme, 0) + 1
        return Token(TOKEN_TYPES["IDENTIFIER"], lexeme, atributo=lexeme)

    def _read_number(self) -> Token:
        chars: list[str] = []
        while self._current() and self._current().isdigit():
            chars.append(self._advance())
        is_float = False
        if self._current() == "." and self._peek().isdigit():
            is_float = True
            chars.append(self._advance())
            while self._current() and self._current().isdigit():
                chars.append(self._advance())
        if self._current() and (self._current().isalpha() or self._current() == "_"):
            while self._current() and (self._current().isalnum() or self._current() == "_"):
                chars.append(self._advance())
            lexeme = "".join(chars)
            msg = (
                f"[Linha {self.line}] Nome de variável começa com número: "
                f"'{lexeme}'. Identificadores devem iniciar com letra ou '_'."
            )
            self.errors.append(msg)
            return Token(TOKEN_TYPES["ERROR"], lexeme, msg)
        lexeme = "".join(chars)
        if is_float:
            return Token(TOKEN_TYPES["FLOAT_LITERAL"], lexeme, atributo=float(lexeme))
        return Token(TOKEN_TYPES["INT_LITERAL"], lexeme, atributo=int(lexeme))

    def _read_char_literal(self) -> Token:
        chars: list[str] = [self._advance()]
        if not self._current():
            msg = f"[Linha {self.line}] Literal de caractere não terminado."
            self.errors.append(msg)
            return Token(TOKEN_TYPES["ERROR"], "".join(chars), msg)
        if self._current() == "\\":
            chars.append(self._advance())
            if self._current():
                chars.append(self._advance())
        else:
            chars.append(self._advance())
        if self._current() == "'":
            chars.append(self._advance())
            lexeme = "".join(chars)
            return Token(TOKEN_TYPES["CHAR_LITERAL"], lexeme, atributo=lexeme[1:-1])
        lexeme = "".join(chars)
        msg = f"[Linha {self.line}] Literal de caractere mal formado: {lexeme!r}."
        self.errors.append(msg)
        return Token(TOKEN_TYPES["ERROR"], lexeme, msg)

    def _read_string_literal(self) -> Token:
        chars: list[str] = [self._advance()]
        while self._current():
            ch = self._current()
            if ch == "\\":
                chars.append(self._advance())
                if self._current():
                    chars.append(self._advance())
                continue
            if ch == '"':
                chars.append(self._advance())
                lexeme = "".join(chars)
                return Token(TOKEN_TYPES["STRING_LITERAL"], lexeme, atributo=lexeme[1:-1])
            if ch == "\n":
                break
            chars.append(self._advance())
        lexeme = "".join(chars)
        msg = f"[Linha {self.line}] String não terminada: {lexeme!r}."
        self.errors.append(msg)
        return Token(TOKEN_TYPES["ERROR"], lexeme, msg)

    def _read_pp_directive(self) -> Token:
        chars: list[str] = []
        while self._current() and self._current() != "\n":
            chars.append(self._advance())
        return Token(TOKEN_TYPES["PP_DIRECTIVE"], "".join(chars))

    def _read_operator(self) -> Token:
        triple = self._current() + self._peek(1) + self._peek(2)
        if len(triple) == 3 and triple in COMPOUND_OPERATORS:
            for _ in range(3):
                self._advance()
            return Token(TOKEN_TYPES["OPERATOR"], triple)
        double = self._current() + self._peek(1)
        if len(double) == 2 and double in COMPOUND_OPERATORS:
            self._advance()
            self._advance()
            return Token(TOKEN_TYPES["OPERATOR"], double)
        ch = self._current()
        if ch in SINGLE_OPERATORS:
            self._advance()
            tipo = (TOKEN_TYPES["DELIMITER"] if ch in DELIMITER_CHARS
                    else TOKEN_TYPES["OPERATOR"])
            return Token(tipo, ch)
        self._advance()
        msg = f"[Linha {self.line}] Caractere inválido: {ch!r}."
        self.errors.append(msg)
        return Token(TOKEN_TYPES["ERROR"], ch, msg)

    def tokenize(self) -> list[Token]:
        num_types = {TOKEN_TYPES["INT_LITERAL"], TOKEN_TYPES["FLOAT_LITERAL"]}

        while self._current():
            if self._current() in (" ", "\t", "\r", "\n"):
                self._skip_whitespace()
                continue
            if self._current() == "/" and self._peek() == "/":
                self._skip_line_comment()
                continue
            if self._current() == "/" and self._peek() == "*":
                self._skip_block_comment()
                continue
            if self._current() == "#":
                self.tokens.append(self._read_pp_directive())
                continue
            if self._current().isalpha() or self._current() == "_":
                self.tokens.append(self._read_identifier_or_keyword())
                continue
            if self._current().isdigit():
                self.tokens.append(self._read_number())
                continue
            if self._current() == "'":
                self.tokens.append(self._read_char_literal())
                continue
            if self._current() == '"':
                self.tokens.append(self._read_string_literal())
                continue
            if self._current() == ",":
                last_is_num = bool(
                    self.tokens and self.tokens[-1].tipo in num_types
                )
                if last_is_num:
                    offset = 1
                    while self._peek(offset) in (" ", "\t"):
                        offset += 1
                    if self._peek(offset).isdigit():
                        ch = self._advance()
                        msg = (
                            f"[Linha {self.line}] Uso incorreto de vírgula como "
                            f"separador decimal. Em C, o separador decimal é o ponto ('.')."
                        )
                        self.errors.append(msg)
                        self.tokens.append(Token(TOKEN_TYPES["ERROR"], ch, msg))
                        continue
            self.tokens.append(self._read_operator())

        self.tokens.append(Token(TOKEN_TYPES["EOF"], ""))
        return self.tokens