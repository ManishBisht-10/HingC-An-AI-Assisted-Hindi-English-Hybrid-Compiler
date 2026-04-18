from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Union

from . import ast_nodes as ast
from .errors import SemanticError, SemanticIssue, SemanticWarning


HingType = str  # "poora" | "dasha" | "akshar" | "shabd" | "khaali"


@dataclass
class SymbolInfo:
    type: HingType
    declared_line: int
    initialized: bool


@dataclass(frozen=True, slots=True)
class FunctionInfo:
    return_type: HingType
    params: List[Tuple[HingType, str]]


class SemanticAnalyzer:
    def __init__(self) -> None:
        self.scopes: List[Dict[str, SymbolInfo]] = []
        self.functions: Dict[str, FunctionInfo] = {}
        self.issues: List[SemanticIssue] = []
        self._loop_depth = 0
        self._current_return_type: Optional[HingType] = None

    def analyze(self, program: ast.Program) -> List[SemanticIssue]:
        self.scopes = [dict()]
        self.functions = {}
        self.issues = []
        self._loop_depth = 0
        self._current_return_type = None

        # Predeclare all functions (allow forward calls)
        for stmt in program.body:
            if isinstance(stmt, ast.FunctionDecl):
                if stmt.name in self.functions:
                    # duplicate function name
                    self._error(1, 1, f"Redeclaration of function '{stmt.name}'")
                else:
                    self.functions[stmt.name] = FunctionInfo(return_type=stmt.return_type, params=stmt.params)

        for stmt in program.body:
            self._visit_stmt(stmt)

        return self.issues

    # -------------------------
    # scope helpers
    # -------------------------

    def _push_scope(self) -> None:
        self.scopes.append({})

    def _pop_scope(self) -> None:
        self.scopes.pop()

    def _declare(self, name: str, info: SymbolInfo, line: int = 1, col: int = 1) -> None:
        scope = self.scopes[-1]
        if name in scope:
            self._error(line, col, f"Redeclaration of variable '{name}' in the same scope")
            return
        scope[name] = info

    def _lookup(self, name: str) -> Optional[SymbolInfo]:
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        return None

    # -------------------------
    # issue helpers
    # -------------------------

    def _error(self, line: int, col: int, msg: str) -> None:
        self.issues.append(SemanticError(msg, line, col))

    def _warn(self, line: int, col: int, msg: str) -> None:
        self.issues.append(SemanticWarning(msg, line, col))

    # -------------------------
    # visitors
    # -------------------------

    def _visit_stmt(self, stmt: ast.Statement) -> None:
        if isinstance(stmt, ast.Block):
            self._push_scope()
            self._visit_block(stmt)
            self._pop_scope()
            return

        if isinstance(stmt, ast.VarDeclaration):
            init = stmt.value is not None
            self._declare(stmt.name, SymbolInfo(type=stmt.type, declared_line=1, initialized=init))
            if stmt.value is not None:
                rhs_t = self._infer_expr_type(stmt.value)
                if rhs_t is not None and not self._is_assignable(stmt.type, rhs_t):
                    self._error(1, 1, f"Type mismatch: cannot assign {rhs_t} to {stmt.type} variable '{stmt.name}'")
            return

        if isinstance(stmt, ast.Assignment):
            sym = self._lookup(stmt.name)
            if sym is None:
                self._error(1, 1, f"Undeclared variable '{stmt.name}'")
            rhs_t = self._infer_expr_type(stmt.value)
            if sym is not None:
                if rhs_t is not None and not self._is_assignable(sym.type, rhs_t):
                    self._error(1, 1, f"Type mismatch: cannot assign {rhs_t} to {sym.type} variable '{stmt.name}'")
                sym.initialized = True
            return

        if isinstance(stmt, ast.IfStatement):
            self._infer_expr_type(stmt.condition)
            self._visit_stmt(stmt.then_body)
            for cond, block in stmt.elif_clauses:
                self._infer_expr_type(cond)
                self._visit_stmt(block)
            if stmt.else_body is not None:
                self._visit_stmt(stmt.else_body)
            return

        if isinstance(stmt, ast.WhileStatement):
            self._infer_expr_type(stmt.condition)
            self._loop_depth += 1
            self._visit_stmt(stmt.body)
            self._loop_depth -= 1
            return

        if isinstance(stmt, ast.ForStatement):
            self._push_scope()
            if stmt.init is not None:
                self._visit_stmt(stmt.init)
            if stmt.condition is not None:
                self._infer_expr_type(stmt.condition)
            self._loop_depth += 1
            self._visit_stmt(stmt.body)
            self._loop_depth -= 1
            if stmt.update is not None:
                self._visit_stmt(stmt.update)
            self._pop_scope()
            return

        if isinstance(stmt, ast.FunctionDecl):
            # new scope for params + body
            prev_ret = self._current_return_type
            self._current_return_type = stmt.return_type
            self._push_scope()
            for ptype, pname in stmt.params:
                self._declare(pname, SymbolInfo(type=ptype, declared_line=1, initialized=True))
            self._visit_block(stmt.body)
            self._pop_scope()
            self._current_return_type = prev_ret
            return

        if isinstance(stmt, ast.ReturnStatement):
            expected = self._current_return_type
            if expected is None:
                # Top-level return is valid in HingC program body.
                return
            if expected == "khaali":
                if stmt.value is not None:
                    self._error(1, 1, "Void (khaali) function cannot return a value")
                return
            if stmt.value is None:
                self._error(1, 1, f"Non-void function must return a value of type {expected}")
                return
            actual = self._infer_expr_type(stmt.value)
            if actual is not None and not self._is_assignable(expected, actual):
                self._error(1, 1, f"Return type mismatch: expected {expected}, got {actual}")
            return

        if isinstance(stmt, ast.PrintStatement):
            self._infer_expr_type(stmt.format_str)
            for a in stmt.args:
                self._infer_expr_type(a)
            return

        if isinstance(stmt, ast.InputStatement):
            self._infer_expr_type(stmt.format_str)
            for v in stmt.variables:
                self._mark_initialized_from_scan_target(v)
            return

        if isinstance(stmt, ast.BreakStatement):
            if self._loop_depth <= 0:
                self._error(1, 1, "Break (toro) used outside of a loop")
            return

        if isinstance(stmt, ast.ContinueStatement):
            if self._loop_depth <= 0:
                self._error(1, 1, "Continue (agla) used outside of a loop")
            return

        if isinstance(stmt, ast.SwitchStatement):
            self._infer_expr_type(stmt.expr)
            self._push_scope()
            for c in stmt.cases:
                self._push_scope()
                self._infer_expr_type(c.value)
                self._visit_stmt(c.body)
                self._pop_scope()
            if stmt.default is not None:
                self._visit_stmt(stmt.default)
            self._pop_scope()
            return

        if isinstance(stmt, ast.ExpressionStatement):
            self._infer_expr_type(stmt.expr)
            return

        # unknown statement type
        self._warn(1, 1, f"Unhandled statement node: {stmt.__class__.__name__}")

    def _visit_block(self, block: ast.Block) -> None:
        saw_return = False
        for st in block.statements:
            if saw_return:
                self._warn(1, 1, "Unreachable code after return")
                break
            self._visit_stmt(st)
            if isinstance(st, ast.ReturnStatement):
                saw_return = True

    # -------------------------
    # expr typing
    # -------------------------

    def _infer_expr_type(self, expr: ast.Expression) -> Optional[HingType]:
        if isinstance(expr, ast.IntLiteral):
            return "poora"
        if isinstance(expr, ast.FloatLiteral):
            return "dasha"
        if isinstance(expr, ast.CharLiteral):
            return "akshar"
        if isinstance(expr, ast.StringLiteral):
            return "shabd"
        if isinstance(expr, ast.Identifier):
            sym = self._lookup(expr.name)
            if sym is None:
                self._error(1, 1, f"Undeclared variable '{expr.name}'")
                return None
            if not sym.initialized:
                self._error(1, 1, f"Variable '{expr.name}' used before initialization")
            return sym.type
        if isinstance(expr, ast.FunctionCall):
            finfo = self.functions.get(expr.name)
            if finfo is None:
                self._error(1, 1, f"Call to undefined function '{expr.name}'")
                # still type-check args
                for a in expr.args:
                    self._infer_expr_type(a)
                return None
            if len(expr.args) != len(finfo.params):
                self._error(
                    1,
                    1,
                    f"Function '{expr.name}' called with wrong number of arguments: expected {len(finfo.params)}, got {len(expr.args)}",
                )
            for a in expr.args:
                self._infer_expr_type(a)
            return finfo.return_type
        if isinstance(expr, ast.UnaryOp):
            t = self._infer_expr_type(expr.operand)
            if expr.op in ("!", "nahi"):
                return "poora"
            if expr.op == "-":
                if t in ("poora", "dasha"):
                    return t
                self._error(1, 1, f"Unary '-' not supported for type {t}")
                return None
            if expr.op == "&":
                # address-of: keep operand type for now (codegen will emit &)
                return t
            return t
        if isinstance(expr, ast.BinaryOp):
            lt = self._infer_expr_type(expr.left)
            rt = self._infer_expr_type(expr.right)
            op = expr.op

            # division by zero (static literal)
            if op == "/" and isinstance(expr.right, ast.IntLiteral) and expr.right.value == 0:
                self._error(1, 1, "Division by zero")
            if op == "/" and isinstance(expr.right, ast.FloatLiteral) and expr.right.value == 0.0:
                self._error(1, 1, "Division by zero")

            if op in ("+", "-", "*", "/", "%"):
                return self._numeric_result_type(lt, rt, op)
            if op in (">", "<", ">=", "<=", "==", "!="):
                return "poora"
            if op in ("&&", "||", "aur", "ya"):
                return "poora"
            return None
        return None

    def _numeric_result_type(self, lt: Optional[HingType], rt: Optional[HingType], op: str) -> Optional[HingType]:
        if lt is None or rt is None:
            return None
        if lt not in ("poora", "dasha") or rt not in ("poora", "dasha"):
            self._error(1, 1, f"Operator '{op}' requires numeric operands, got {lt} and {rt}")
            return None
        if lt == "dasha" or rt == "dasha":
            return "dasha"
        return "poora"

    def _is_assignable(self, target: HingType, source: HingType) -> bool:
        if target == source:
            return True
        # allow implicit int -> float
        if target == "dasha" and source == "poora":
            return True
        return False

    def _mark_initialized_from_scan_target(self, expr: ast.Expression) -> None:
        # lo("%d", &x) or lo("%d", x) - both should mark x initialized
        if isinstance(expr, ast.Identifier):
            sym = self._lookup(expr.name)
            if sym is None:
                self._error(1, 1, f"Undeclared variable '{expr.name}'")
                return
            sym.initialized = True
            return
        if isinstance(expr, ast.UnaryOp) and expr.op == "&" and isinstance(expr.operand, ast.Identifier):
            sym = self._lookup(expr.operand.name)
            if sym is None:
                self._error(1, 1, f"Undeclared variable '{expr.operand.name}'")
                return
            sym.initialized = True
            return
        self._error(1, 1, "Invalid input target in lo(...): expected variable or &variable")


def analyze(program: ast.Program) -> List[SemanticIssue]:
    return SemanticAnalyzer().analyze(program)

