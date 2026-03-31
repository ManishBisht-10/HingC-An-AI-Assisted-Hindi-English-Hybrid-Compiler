from __future__ import annotations

from dataclasses import dataclass
from typing import Any, List, Optional, Sequence, Tuple, Union


class ASTNode:
    """Base class for all AST nodes."""

    __slots__ = ()

    def __repr__(self) -> str:  # pragma: no cover (exercised indirectly)
        return _ast_repr(self)


class Statement(ASTNode):
    __slots__ = ()


class Expression(ASTNode):
    __slots__ = ()


# -------------------------
# Program / blocks
# -------------------------


@dataclass(frozen=True, slots=True)
class Program(ASTNode):
    body: List[Statement]


@dataclass(frozen=True, slots=True)
class Block(Statement):
    statements: List[Statement]


# -------------------------
# Statements
# -------------------------


@dataclass(frozen=True, slots=True)
class VarDeclaration(Statement):
    type: str
    name: str
    value: Optional[Expression] = None


@dataclass(frozen=True, slots=True)
class Assignment(Statement):
    name: str
    value: Expression


@dataclass(frozen=True, slots=True)
class IfStatement(Statement):
    condition: Expression
    then_body: Block
    elif_clauses: List[Tuple[Expression, Block]]
    else_body: Optional[Block]


@dataclass(frozen=True, slots=True)
class WhileStatement(Statement):
    condition: Expression
    body: Block


@dataclass(frozen=True, slots=True)
class ForStatement(Statement):
    init: Optional[Statement]
    condition: Optional[Expression]
    update: Optional[Statement]
    body: Block


@dataclass(frozen=True, slots=True)
class FunctionDecl(Statement):
    return_type: str
    name: str
    params: List[Tuple[str, str]]  # (type, name)
    body: Block


@dataclass(frozen=True, slots=True)
class ReturnStatement(Statement):
    value: Optional[Expression] = None


@dataclass(frozen=True, slots=True)
class PrintStatement(Statement):
    format_str: Expression  # typically StringLiteral, but allow expression
    args: List[Expression]


@dataclass(frozen=True, slots=True)
class InputStatement(Statement):
    format_str: Expression  # typically StringLiteral
    variables: List[Expression]  # typically Identifier (or unary & forms later)


@dataclass(frozen=True, slots=True)
class BreakStatement(Statement):
    pass


@dataclass(frozen=True, slots=True)
class ContinueStatement(Statement):
    pass


@dataclass(frozen=True, slots=True)
class SwitchStatement(Statement):
    expr: Expression
    cases: List["CaseClause"]
    default: Optional[Block]


@dataclass(frozen=True, slots=True)
class CaseClause(ASTNode):
    value: Expression
    body: Block


# Expression-as-statement (function calls)
@dataclass(frozen=True, slots=True)
class ExpressionStatement(Statement):
    expr: Expression


# -------------------------
# Expressions
# -------------------------


@dataclass(frozen=True, slots=True)
class BinaryOp(Expression):
    left: Expression
    op: str
    right: Expression


@dataclass(frozen=True, slots=True)
class UnaryOp(Expression):
    op: str
    operand: Expression


@dataclass(frozen=True, slots=True)
class Identifier(Expression):
    name: str


@dataclass(frozen=True, slots=True)
class FunctionCall(Expression):
    name: str
    args: List[Expression]


@dataclass(frozen=True, slots=True)
class IntLiteral(Expression):
    value: int


@dataclass(frozen=True, slots=True)
class FloatLiteral(Expression):
    value: float


@dataclass(frozen=True, slots=True)
class StringLiteral(Expression):
    value: str


@dataclass(frozen=True, slots=True)
class CharLiteral(Expression):
    value: str  # single character


def _ast_repr(node: Any) -> str:
    """
    Stable, readable repr for all AST nodes.

    - Prints class name with keyword fields.
    - Formats lists/tuples recursively.
    - Keeps strings quoted.
    """

    def fmt(v: Any) -> str:
        if isinstance(v, ASTNode):
            return _ast_repr(v)
        if isinstance(v, str):
            return repr(v)
        if isinstance(v, (int, float, bool, type(None))):
            return repr(v)
        if isinstance(v, list):
            return "[" + ", ".join(fmt(x) for x in v) + "]"
        if isinstance(v, tuple):
            return "(" + ", ".join(fmt(x) for x in v) + ")"
        return repr(v)

    cls = node.__class__.__name__
    if hasattr(node, "__dataclass_fields__"):
        parts = []
        for k in node.__dataclass_fields__.keys():  # type: ignore[attr-defined]
            parts.append(f"{k}={fmt(getattr(node, k))}")
        return f"{cls}(" + ", ".join(parts) + ")"
    return f"{cls}()"


__all__ = [
    # base
    "ASTNode",
    "Statement",
    "Expression",
    # program
    "Program",
    "Block",
    # statements
    "VarDeclaration",
    "Assignment",
    "IfStatement",
    "WhileStatement",
    "ForStatement",
    "FunctionDecl",
    "ReturnStatement",
    "PrintStatement",
    "InputStatement",
    "BreakStatement",
    "ContinueStatement",
    "SwitchStatement",
    "CaseClause",
    "ExpressionStatement",
    # expressions
    "BinaryOp",
    "UnaryOp",
    "Identifier",
    "FunctionCall",
    "IntLiteral",
    "FloatLiteral",
    "StringLiteral",
    "CharLiteral",
]

