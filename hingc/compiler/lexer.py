from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .errors import LexerError


@dataclass(frozen=True, slots=True)
class Token:
    type: str
    value: str
    line: int
    column: int


KEYWORDS = {
    "shuru",
    "khatam",
    "rakho",
    "agar",
    "warna",
    "jabtak",
    "karo",
    "kaam",
    "wapas",
    "likho",
    "lo",
    "toro",
    "agla",
    "chunao",
    "sthiti",
    "warna_default",
    "poora",
    "dasha",
    "akshar",
    "shabd",
    "khaali",
    "sahi",
    "galat",
}

MULTIWORD_KEYWORDS = {
    ("warna", "agar"): "warna agar",
}

LOGICAL_KEYWORDS = {"aur", "ya", "nahi"}


_SINGLE_CHAR_TOKENS = {
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ",": "COMMA",
    ":": "COLON",
    ";": "SEMICOLON",
}

_TWO_CHAR_OPERATORS = {
    ">=": "COMPARISON",
    "<=": "COMPARISON",
    "==": "COMPARISON",
    "!=": "COMPARISON",
    "&&": "LOGICAL",
    "||": "LOGICAL",
}

_ONE_CHAR_OPERATORS = {
    "=": "ASSIGN",
    "+": "OPERATOR",
    "-": "OPERATOR",
    "*": "OPERATOR",
    "/": "OPERATOR",
    "%": "OPERATOR",
    "&": "OPERATOR",
    ">": "COMPARISON",
    "<": "COMPARISON",
    "!": "LOGICAL",
}


class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.i = 0
        self.line = 1
        self.col = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while not self._eof():
            ch = self._peek()

            # Whitespace (except newline)
            if ch in (" ", "\t", "\r"):
                self._advance()
                continue

            # Newlines are meaningful for error reporting / optional parsing
            if ch == "\n":
                tokens.append(Token("NEWLINE", "\n", self.line, self.col))
                self._advance_newline()
                continue

            # Comments
            if ch == "/":
                nxt = self._peek(1)
                if nxt == "/":
                    self._skip_line_comment()
                    continue
                if nxt == "*":
                    self._skip_block_comment()
                    continue

            # String literal
            if ch == '"':
                tokens.append(self._read_string())
                continue

            # Char literal
            if ch == "'":
                tokens.append(self._read_char())
                continue

            # Identifiers / keywords (allow unicode in identifier body)
            if self._is_ident_start(ch):
                tokens.append(self._read_identifier_or_keyword())
                continue

            # Number literals
            if ch.isdigit():
                tokens.append(self._read_number())
                continue

            # Two-char operators
            two = (ch + self._peek(1)) if not self._eof(1) else ""
            if two in _TWO_CHAR_OPERATORS:
                tokens.append(Token(_TWO_CHAR_OPERATORS[two], two, self.line, self.col))
                self._advance()
                self._advance()
                continue

            # Single-char tokens like parens/braces etc
            if ch in _SINGLE_CHAR_TOKENS:
                tokens.append(Token(_SINGLE_CHAR_TOKENS[ch], ch, self.line, self.col))
                self._advance()
                continue

            # One-char operators
            if ch in _ONE_CHAR_OPERATORS:
                tokens.append(Token(_ONE_CHAR_OPERATORS[ch], ch, self.line, self.col))
                self._advance()
                continue

            raise LexerError(f"Invalid character: {ch!r}", self.line, self.col)

        tokens.append(Token("EOF", "", self.line, self.col))
        return tokens

    # ---------------------
    # core cursor helpers
    # ---------------------

    def _eof(self, lookahead: int = 0) -> bool:
        return self.i + lookahead >= len(self.source)

    def _peek(self, lookahead: int = 0) -> str:
        if self._eof(lookahead):
            return "\0"
        return self.source[self.i + lookahead]

    def _advance(self) -> str:
        ch = self.source[self.i]
        self.i += 1
        self.col += 1
        return ch

    def _advance_newline(self) -> None:
        self.i += 1
        self.line += 1
        self.col = 1

    # ---------------------
    # comments
    # ---------------------

    def _skip_line_comment(self) -> None:
        # consume leading //
        self._advance()
        self._advance()
        while not self._eof() and self._peek() != "\n":
            self._advance()

    def _skip_block_comment(self) -> None:
        # consume leading /*
        start_line, start_col = self.line, self.col
        self._advance()
        self._advance()
        while not self._eof():
            if self._peek() == "\n":
                self._advance_newline()
                continue
            if self._peek() == "*" and self._peek(1) == "/":
                self._advance()
                self._advance()
                return
            self._advance()
        raise LexerError("Unterminated block comment", start_line, start_col)

    # ---------------------
    # literals
    # ---------------------

    def _read_string(self) -> Token:
        start_line, start_col = self.line, self.col
        self._advance()  # opening "
        value_chars: List[str] = []
        while not self._eof():
            ch = self._peek()
            if ch == "\n":
                raise LexerError("Unterminated string literal", start_line, start_col)
            if ch == '"':
                self._advance()
                return Token("STRING_LITERAL", "".join(value_chars), start_line, start_col)
            if ch == "\\":
                value_chars.append(self._read_escape_sequence(start_line, start_col))
                continue
            value_chars.append(self._advance())
        raise LexerError("Unterminated string literal", start_line, start_col)

    def _read_char(self) -> Token:
        start_line, start_col = self.line, self.col
        self._advance()  # opening '
        if self._eof():
            raise LexerError("Unterminated char literal", start_line, start_col)
        ch = self._peek()
        if ch == "\n":
            raise LexerError("Unterminated char literal", start_line, start_col)
        if ch == "\\":
            val = self._read_escape_sequence(start_line, start_col)
        else:
            val = self._advance()
        if self._peek() != "'":
            raise LexerError("Unterminated char literal", start_line, start_col)
        self._advance()  # closing '
        if len(val) != 1:
            raise LexerError("Invalid char literal", start_line, start_col)
        return Token("CHAR_LITERAL", val, start_line, start_col)

    def _read_escape_sequence(self, start_line: int, start_col: int) -> str:
        self._advance()  # consume backslash
        if self._eof():
            raise LexerError("Unterminated escape sequence", start_line, start_col)
        esc = self._advance()
        mapping = {
            "n": "\n",
            "t": "\t",
            "r": "\r",
            "\\": "\\",
            '"': '"',
            "'": "'",
            "0": "\0",
        }
        return mapping.get(esc, esc)

    def _read_number(self) -> Token:
        start_line, start_col = self.line, self.col
        digits: List[str] = []
        while self._peek().isdigit():
            digits.append(self._advance())
        if self._peek() == "." and self._peek(1).isdigit():
            digits.append(self._advance())  # '.'
            while self._peek().isdigit():
                digits.append(self._advance())
            return Token("NUMBER_FLOAT", "".join(digits), start_line, start_col)
        return Token("NUMBER_INT", "".join(digits), start_line, start_col)

    # ---------------------
    # identifiers / keywords
    # ---------------------

    def _is_ident_start(self, ch: str) -> bool:
        return ch.isalpha() or ch == "_" or ord(ch) >= 128

    def _is_ident_part(self, ch: str) -> bool:
        return ch.isalnum() or ch == "_" or ord(ch) >= 128

    def _read_identifier_or_keyword(self) -> Token:
        start_line, start_col = self.line, self.col
        first = self._read_identifier_text()

        # Multi-word keyword: "warna agar"
        if (first,) == ("warna",):
            save_i, save_line, save_col = self.i, self.line, self.col
            self._skip_inline_spaces()
            if self._is_ident_start(self._peek()):
                second = self._read_identifier_text()
                key = (first, second)
                if key in MULTIWORD_KEYWORDS:
                    return Token("KEYWORD", MULTIWORD_KEYWORDS[key], start_line, start_col)
            # rollback if not matching
            self.i, self.line, self.col = save_i, save_line, save_col

        if first in LOGICAL_KEYWORDS:
            return Token("LOGICAL", first, start_line, start_col)
        if first in KEYWORDS:
            return Token("KEYWORD", first, start_line, start_col)
        return Token("IDENTIFIER", first, start_line, start_col)

    def _read_identifier_text(self) -> str:
        buf: List[str] = []
        while self._is_ident_part(self._peek()):
            buf.append(self._advance())
        return "".join(buf)

    def _skip_inline_spaces(self) -> None:
        while self._peek() in (" ", "\t", "\r"):
            self._advance()


def lex(source: str) -> List[Token]:
    return Lexer(source).tokenize()

