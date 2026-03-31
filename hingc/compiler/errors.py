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


@dataclass(frozen=True, slots=True)
class SemanticIssue(CompilerError):
    severity: str  # "error" | "warning"

    def __init__(self, message: str, line: int, column: int, severity: str):
        super().__init__(message=message, line=line, column=column, phase="semantic")
        object.__setattr__(self, "severity", severity)

    def __str__(self) -> str:
        return f"[semantic/{self.severity}] Line {self.line}, Col {self.column}: {self.message}"


@dataclass(frozen=True, slots=True)
class SemanticError(SemanticIssue):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message=message, line=line, column=column, severity="error")


@dataclass(frozen=True, slots=True)
class SemanticWarning(SemanticIssue):
    def __init__(self, message: str, line: int, column: int):
        super().__init__(message=message, line=line, column=column, severity="warning")

