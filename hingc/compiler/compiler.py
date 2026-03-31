from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .ast_nodes import Program
from .codegen import generate_c
from .errors import CompilerError, LexerError, ParseError, SemanticError, SemanticIssue
from .lexer import Token, lex
from .parser import Parser
from .semantic import analyze


@dataclass(frozen=True, slots=True)
class CompilationResult:
    success: bool
    tokens: List[Token]
    ast: Optional[Program]
    semantic_errors: List[SemanticError]
    generated_c_code: Optional[str]
    errors: List[CompilerError]
    warnings: List[str]
    phase_failed: Optional[str]  # "lexer" | "parser" | "semantic" | None


class HingCCompiler:
    def compile(self, source: str) -> CompilationResult:
        tokens: List[Token] = []
        ast: Optional[Program] = None
        semantic_issues: List[SemanticIssue] = []
        generated: Optional[str] = None
        errors: List[CompilerError] = []
        warnings: List[str] = []
        phase_failed: Optional[str] = None

        # 1) Lex
        try:
            tokens = lex(source)
        except LexerError as e:
            errors.append(e)
            phase_failed = "lexer"
            return CompilationResult(
                success=False,
                tokens=[],
                ast=None,
                semantic_errors=[],
                generated_c_code=None,
                errors=errors,
                warnings=[],
                phase_failed=phase_failed,
            )

        # 2) Parse
        try:
            ast = Parser(tokens).parse()
        except ParseError as e:
            errors.append(e)
            phase_failed = "parser"
            return CompilationResult(
                success=False,
                tokens=tokens,
                ast=None,
                semantic_errors=[],
                generated_c_code=None,
                errors=errors,
                warnings=[],
                phase_failed=phase_failed,
            )

        # 3) Semantic
        semantic_issues = analyze(ast)
        semantic_errors = [i for i in semantic_issues if isinstance(i, SemanticError)]
        semantic_warnings = [i for i in semantic_issues if not isinstance(i, SemanticError)]
        errors.extend(semantic_errors)
        warnings.extend(str(w) for w in semantic_warnings)

        if semantic_errors:
            phase_failed = "semantic"
            return CompilationResult(
                success=False,
                tokens=tokens,
                ast=ast,
                semantic_errors=semantic_errors,
                generated_c_code=None,
                errors=errors,
                warnings=warnings,
                phase_failed=phase_failed,
            )

        # 4) Codegen
        generated = generate_c(ast)

        return CompilationResult(
            success=True,
            tokens=tokens,
            ast=ast,
            semantic_errors=[],
            generated_c_code=generated,
            errors=[],
            warnings=warnings,
            phase_failed=None,
        )

