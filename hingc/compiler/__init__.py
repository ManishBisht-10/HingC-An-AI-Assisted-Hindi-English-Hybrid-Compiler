"""Compiler core for the HingC language.

This module re-exports the commonly used compiler entrypoints so tests
and external callers can import from ``hingc.compiler`` directly.
"""

from .lexer import lex, Token
from .parser import Parser, parse
from .codegen import generate_c


def tokenize(source: str):
    """Compatibility wrapper around `lex`.

    The underlying lexer uses uppercase token type names (e.g. "KEYWORD").
    Some integration tests expect keyword tokens to have type "keyword"
    (lowercase) while unit tests expect other token types unchanged. This
    wrapper normalizes only keyword tokens to the legacy lowercase shape.
    """
    toks = lex(source)
    out = []
    for t in toks:
        if t.type == "KEYWORD":
            out.append(Token("keyword", t.value, t.line, t.column))
        else:
            out.append(t)
    return out


def compile_to_c(ast, tokens=None):
    """Compatibility wrapper: tests call compile_to_c(ast, tokens).

    The underlying `generate_c` only needs the AST; accept an optional
    `tokens` argument for backward compatibility.
    """
    return generate_c(ast)


__all__ = ["tokenize", "Token", "Parser", "parse", "compile_to_c"]
