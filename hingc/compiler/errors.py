from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CompilerError(Exception):
    message: str
    line: int
    column: int
    phase: str

    def __str__(self) -> str:
        return f"[{self.phase}] Line {self.line}, Col {self.column}: {self.message}"


@dataclass(frozen=True, slots=True)
class LexerError(CompilerError):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message=message, line=line, column=column, phase="lexer")


@dataclass(frozen=True, slots=True)
class ParseError(CompilerError):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message=message, line=line, column=column, phase="parser")

