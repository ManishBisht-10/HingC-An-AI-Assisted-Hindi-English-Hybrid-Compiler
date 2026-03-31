from __future__ import annotations

from typing import List, Optional, Tuple

from .ast_nodes import (
    Assignment,
    BinaryOp,
    Block,
    BreakStatement,
    CaseClause,
    CharLiteral,
    ContinueStatement,
    Expression,
    ExpressionStatement,
    FloatLiteral,
    ForStatement,
    FunctionCall,
    FunctionDecl,
    Identifier,
    IfStatement,
    InputStatement,
    IntLiteral,
    PrintStatement,
    Program,
    ReturnStatement,
    Statement,
    StringLiteral,
    SwitchStatement,
    UnaryOp,
    VarDeclaration,
    WhileStatement,
)
from .errors import ParseError
from .lexer import Token, lex


TYPE_KEYWORDS = {"poora", "dasha", "akshar", "shabd", "khaali"}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.i = 0

    def parse(self) -> Program:
        self._skip_separators()
        self._expect_keyword("shuru")
        self._skip_separators()

        body: List[Statement] = []
        while not self._is_keyword("khatam") and not self._at("EOF"):
            if self._at("NEWLINE"):
                self._advance()
                continue
            body.append(self._parse_statement())
            self._skip_statement_terminators()

        self._expect_keyword("khatam")
        self._skip_separators()
        self._expect("EOF")
        return Program(body=body)

    # -------------------------
    # statements
    # -------------------------

    def _parse_statement(self) -> Statement:
        tok = self._peek()

        if self._is_keyword("rakho"):
            return self._parse_var_decl()
        if self._is_keyword("agar"):
            return self._parse_if()
        if self._is_keyword("jabtak"):
            return self._parse_while()
        if self._is_keyword("karo"):
            return self._parse_for()
        if self._is_keyword("kaam"):
            return self._parse_function_decl()
        if self._is_keyword("wapas"):
            return self._parse_return()
        if self._is_keyword("likho"):
            return self._parse_print()
        if self._is_keyword("lo"):
            return self._parse_input()
        if self._is_keyword("toro"):
            self._advance()
            return BreakStatement()
        if self._is_keyword("agla"):
            self._advance()
            return ContinueStatement()
        if self._is_keyword("chunao"):
            return self._parse_switch()

        # Assignment or expression statement (function call)
        if tok.type == "IDENTIFIER":
            if self._peek(1).type == "ASSIGN":
                return self._parse_assignment()
            expr = self._parse_expression()
            return ExpressionStatement(expr=expr)

        raise self._error_here(f"Unexpected token {tok.type}({tok.value!r}) in statement")

    def _parse_var_decl(self) -> VarDeclaration:
        self._expect_keyword("rakho")
        type_tok = self._expect("KEYWORD")
        if type_tok.value not in TYPE_KEYWORDS:
            raise self._error_at(type_tok, f"Expected type keyword, got {type_tok.value!r}")
        name_tok = self._expect("IDENTIFIER")
        value: Optional[Expression] = None
        if self._at("ASSIGN"):
            self._advance()
            value = self._parse_expression()
        return VarDeclaration(type=type_tok.value, name=name_tok.value, value=value)

    def _parse_assignment(self) -> Assignment:
        name_tok = self._expect("IDENTIFIER")
        self._expect("ASSIGN")
        value = self._parse_expression()
        return Assignment(name=name_tok.value, value=value)

    def _parse_if(self) -> IfStatement:
        self._expect_keyword("agar")
        self._expect("LPAREN")
        cond = self._parse_expression()
        self._expect("RPAREN")
        then_body = self._parse_block()

        elifs: List[Tuple[Expression, Block]] = []
        while self._is_keyword("warna agar"):
            self._advance()  # KEYWORD "warna agar"
            self._expect("LPAREN")
            econd = self._parse_expression()
            self._expect("RPAREN")
            ebody = self._parse_block()
            elifs.append((econd, ebody))

        else_body: Optional[Block] = None
        if self._is_keyword("warna"):
            self._advance()
            else_body = self._parse_block()

        return IfStatement(condition=cond, then_body=then_body, elif_clauses=elifs, else_body=else_body)

    def _parse_while(self) -> WhileStatement:
        self._expect_keyword("jabtak")
        self._expect("LPAREN")
        cond = self._parse_expression()
        self._expect("RPAREN")
        body = self._parse_block()
        return WhileStatement(condition=cond, body=body)

    def _parse_for(self) -> ForStatement:
        self._expect_keyword("karo")
        self._expect("LPAREN")

        init: Optional[Statement] = None
        if not self._at("SEMICOLON"):
            if self._is_keyword("rakho"):
                init = self._parse_var_decl()
            elif self._at("IDENTIFIER") and self._peek(1).type == "ASSIGN":
                init = self._parse_assignment()
            else:
                # allow expression statement as init
                init = ExpressionStatement(expr=self._parse_expression())
        self._expect("SEMICOLON")

        cond: Optional[Expression] = None
        if not self._at("SEMICOLON"):
            cond = self._parse_expression()
        self._expect("SEMICOLON")

        update: Optional[Statement] = None
        if not self._at("RPAREN"):
            if self._at("IDENTIFIER") and self._peek(1).type == "ASSIGN":
                update = self._parse_assignment()
            else:
                update = ExpressionStatement(expr=self._parse_expression())
        self._expect("RPAREN")
        body = self._parse_block()
        return ForStatement(init=init, condition=cond, update=update, body=body)

    def _parse_function_decl(self) -> FunctionDecl:
        self._expect_keyword("kaam")
        ret_tok = self._expect("KEYWORD")
        if ret_tok.value not in TYPE_KEYWORDS:
            raise self._error_at(ret_tok, f"Expected return type, got {ret_tok.value!r}")
        name_tok = self._expect("IDENTIFIER")
        self._expect("LPAREN")
        params: List[Tuple[str, str]] = []
        if not self._at("RPAREN"):
            while True:
                ptype = self._expect("KEYWORD")
                if ptype.value not in TYPE_KEYWORDS:
                    raise self._error_at(ptype, f"Expected param type, got {ptype.value!r}")
                pname = self._expect("IDENTIFIER")
                params.append((ptype.value, pname.value))
                if self._at("COMMA"):
                    self._advance()
                    continue
                break
        self._expect("RPAREN")
        body = self._parse_block()
        return FunctionDecl(return_type=ret_tok.value, name=name_tok.value, params=params, body=body)

    def _parse_return(self) -> ReturnStatement:
        self._expect_keyword("wapas")
        if self._at_statement_end():
            return ReturnStatement(value=None)
        return ReturnStatement(value=self._parse_expression())

    def _parse_print(self) -> PrintStatement:
        self._expect_keyword("likho")
        self._expect("LPAREN")
        fmt = self._parse_expression()
        args: List[Expression] = []
        if self._at("COMMA"):
            self._advance()
            args.append(self._parse_expression())
            while self._at("COMMA"):
                self._advance()
                args.append(self._parse_expression())
        self._expect("RPAREN")
        return PrintStatement(format_str=fmt, args=args)

    def _parse_input(self) -> InputStatement:
        self._expect_keyword("lo")
        self._expect("LPAREN")
        fmt = self._parse_expression()
        variables: List[Expression] = []
        if self._at("COMMA"):
            self._advance()
            variables.append(self._parse_expression())
            while self._at("COMMA"):
                self._advance()
                variables.append(self._parse_expression())
        self._expect("RPAREN")
        return InputStatement(format_str=fmt, variables=variables)

    def _parse_switch(self) -> SwitchStatement:
        self._expect_keyword("chunao")
        self._expect("LPAREN")
        expr = self._parse_expression()
        self._expect("RPAREN")
        self._skip_separators()
        self._expect("LBRACE")
        self._skip_separators()

        cases: List[CaseClause] = []
        default_block: Optional[Block] = None

        while not self._at("RBRACE") and not self._at("EOF"):
            if self._is_keyword("sthiti"):
                self._advance()
                val = self._parse_expression()
                self._expect("COLON")
                body_stmts: List[Statement] = []
                self._skip_statement_terminators()
                while not self._at("RBRACE") and not self._at("EOF") and not self._is_keyword("sthiti") and not self._is_keyword(
                    "warna_default"
                ):
                    body_stmts.append(self._parse_statement())
                    self._skip_statement_terminators()
                cases.append(CaseClause(value=val, body=Block(statements=body_stmts)))
                continue

            if self._is_keyword("warna_default"):
                self._advance()
                self._expect("COLON")
                body_stmts = []
                self._skip_statement_terminators()
                while not self._at("RBRACE") and not self._at("EOF") and not self._is_keyword("sthiti"):
                    if self._is_keyword("warna_default"):
                        raise self._error_here("Duplicate warna_default in switch")
                    body_stmts.append(self._parse_statement())
                    self._skip_statement_terminators()
                default_block = Block(statements=body_stmts)
                continue

            if self._at("NEWLINE"):
                self._advance()
                continue

            raise self._error_here("Expected 'sthiti' or 'warna_default' in switch")

        self._expect("RBRACE")
        return SwitchStatement(expr=expr, cases=cases, default=default_block)

    def _parse_block(self) -> Block:
        self._skip_separators()
        self._expect("LBRACE")
        self._skip_separators()
        stmts: List[Statement] = []
        while not self._at("RBRACE") and not self._at("EOF"):
            if self._at("NEWLINE"):
                self._advance()
                continue
            stmts.append(self._parse_statement())
            self._skip_statement_terminators()
        self._expect("RBRACE")
        return Block(statements=stmts)

    # -------------------------
    # expressions (precedence)
    # -------------------------

    def _parse_expression(self) -> Expression:
        return self._parse_or()

    def _parse_or(self) -> Expression:
        expr = self._parse_and()
        while self._match_logical("||") or self._match_logical("ya"):
            op_tok = self._previous()
            right = self._parse_and()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_and(self) -> Expression:
        expr = self._parse_equality()
        while self._match_logical("&&") or self._match_logical("aur"):
            op_tok = self._previous()
            right = self._parse_equality()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_equality(self) -> Expression:
        expr = self._parse_comparison()
        while self._at("COMPARISON") and self._peek().value in ("==", "!="):
            op_tok = self._advance()
            right = self._parse_comparison()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_comparison(self) -> Expression:
        expr = self._parse_term()
        while self._at("COMPARISON") and self._peek().value in (">", "<", ">=", "<="):
            op_tok = self._advance()
            right = self._parse_term()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_term(self) -> Expression:
        expr = self._parse_factor()
        while self._at("OPERATOR") and self._peek().value in ("+", "-"):
            op_tok = self._advance()
            right = self._parse_factor()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_factor(self) -> Expression:
        expr = self._parse_unary()
        while self._at("OPERATOR") and self._peek().value in ("*", "/", "%"):
            op_tok = self._advance()
            right = self._parse_unary()
            expr = BinaryOp(left=expr, op=op_tok.value, right=right)
        return expr

    def _parse_unary(self) -> Expression:
        if (self._at("LOGICAL") and self._peek().value in ("!", "nahi")) or (self._at("OPERATOR") and self._peek().value in ("-", "&")):
            op_tok = self._advance()
            operand = self._parse_unary()
            return UnaryOp(op=op_tok.value, operand=operand)
        return self._parse_primary()

    def _parse_primary(self) -> Expression:
        tok = self._peek()

        if tok.type == "NUMBER_INT":
            self._advance()
            return IntLiteral(value=int(tok.value))
        if tok.type == "NUMBER_FLOAT":
            self._advance()
            return FloatLiteral(value=float(tok.value))
        if tok.type == "STRING_LITERAL":
            self._advance()
            return StringLiteral(value=tok.value)
        if tok.type == "CHAR_LITERAL":
            self._advance()
            return CharLiteral(value=tok.value)

        if tok.type == "KEYWORD" and tok.value in ("sahi", "galat"):
            self._advance()
            return IntLiteral(value=1 if tok.value == "sahi" else 0)

        if tok.type == "IDENTIFIER":
            self._advance()
            ident = tok.value
            if self._at("LPAREN"):
                self._advance()
                args: List[Expression] = []
                if not self._at("RPAREN"):
                    args.append(self._parse_expression())
                    while self._at("COMMA"):
                        self._advance()
                        args.append(self._parse_expression())
                self._expect("RPAREN")
                return FunctionCall(name=ident, args=args)
            return Identifier(name=ident)

        if self._at("LPAREN"):
            self._advance()
            expr = self._parse_expression()
            self._expect("RPAREN")
            return expr

        raise self._error_here(f"Expected expression, got {tok.type}({tok.value!r})")

    # -------------------------
    # utilities
    # -------------------------

    def _skip_separators(self) -> None:
        while self._at("NEWLINE") or self._at("SEMICOLON"):
            self._advance()

    def _skip_statement_terminators(self) -> None:
        # allow many NEWLINE/SEMICOLON between statements
        self._skip_separators()

    def _at_statement_end(self) -> bool:
        return self._at("NEWLINE") or self._at("SEMICOLON") or self._at("RBRACE") or self._at("EOF")

    def _at(self, typ: str) -> bool:
        return self._peek().type == typ

    def _is_keyword(self, value: str) -> bool:
        return self._peek().type == "KEYWORD" and self._peek().value == value

    def _expect_keyword(self, value: str) -> Token:
        tok = self._peek()
        if tok.type == "KEYWORD" and tok.value == value:
            return self._advance()
        raise self._error_at(tok, f"Expected keyword {value!r}")

    def _expect(self, typ: str) -> Token:
        tok = self._peek()
        if tok.type == typ:
            return self._advance()
        raise self._error_at(tok, f"Expected token {typ}, got {tok.type}({tok.value!r})")

    def _match_logical(self, value: str) -> bool:
        tok = self._peek()
        if tok.type == "LOGICAL" and tok.value == value:
            self._advance()
            return True
        return False

    def _peek(self, lookahead: int = 0) -> Token:
        idx = self.i + lookahead
        if idx >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[idx]

    def _advance(self) -> Token:
        tok = self._peek()
        self.i = min(self.i + 1, len(self.tokens) - 1)
        return tok

    def _previous(self) -> Token:
        return self.tokens[max(0, self.i - 1)]

    def _error_here(self, message: str) -> ParseError:
        return self._error_at(self._peek(), message)

    def _error_at(self, tok: Token, message: str) -> ParseError:
        return ParseError(message, tok.line, tok.column)


def parse(source: str) -> Program:
    return Parser(lex(source)).parse()


