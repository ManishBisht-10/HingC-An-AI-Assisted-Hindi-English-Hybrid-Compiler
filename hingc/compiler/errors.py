from __future__ import annotations


class CompilerError(Exception):
    def __init__(self, message: str, line: int, column: int, phase: str) -> None:
        super().__init__(message)
        self.message = message
        self.line = line
        self.column = column
        self.phase = phase

    def __str__(self) -> str:
        return f"[{self.phase}] Line {self.line}, Col {self.column}: {self.message}"


class LexerError(CompilerError):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message=message, line=line, column=column, phase="lexer")


class ParseError(CompilerError):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message=message, line=line, column=column, phase="parser")


class SemanticIssue(CompilerError):
    def __init__(self, message: str, line: int, column: int, severity: str) -> None:
        super().__init__(message=message, line=line, column=column, phase="semantic")
        self.severity = severity

    def __str__(self) -> str:
        return f"[semantic/{self.severity}] Line {self.line}, Col {self.column}: {self.message}"


class SemanticError(SemanticIssue):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message=message, line=line, column=column, severity="error")


class SemanticWarning(SemanticIssue):
    def __init__(self, message: str, line: int, column: int) -> None:
        super().__init__(message=message, line=line, column=column, severity="warning")
