import pytest

from hingc.compiler.errors import ParseError
from hingc.compiler.parser import parse


def test_variable_declaration():
    ast = parse("shuru\nrakho poora x = 10\nkhatam\n")
    assert ast.body[0].__class__.__name__ == "VarDeclaration"
    assert ast.body[0].name == "x"


def test_if_else_parsing():
    src = """shuru
rakho poora x = 10
agar (x > 5) {
  likho("Bada\\n")
} warna {
  likho("Chota\\n")
}
khatam
"""
    ast = parse(src)
    ifs = next(s for s in ast.body if s.__class__.__name__ == "IfStatement")
    assert ifs.then_body.statements
    assert ifs.else_body is not None


def test_while_loop():
    src = """shuru
rakho poora i = 0
jabtak (i < 5) {
  i = i + 1
}
khatam
"""
    ast = parse(src)
    wh = next(s for s in ast.body if s.__class__.__name__ == "WhileStatement")
    assert wh.body.statements


def test_for_loop():
    src = """shuru
karo (rakho poora i = 0 ; i < 10 ; i = i + 1) {
  likho("%d\\n", i)
}
khatam
"""
    ast = parse(src)
    fr = next(s for s in ast.body if s.__class__.__name__ == "ForStatement")
    assert fr.init is not None
    assert fr.condition is not None
    assert fr.update is not None


def test_function_declaration():
    src = """shuru
kaam poora jodo(poora a, poora b) {
  wapas a + b
}
khatam
"""
    ast = parse(src)
    fn = next(s for s in ast.body if s.__class__.__name__ == "FunctionDecl")
    assert fn.name == "jodo"
    assert len(fn.params) == 2


def test_nested_blocks():
    src = """shuru
agar (1 == 1) {
  agar (2 == 2) {
    likho("ok\\n")
  }
}
khatam
"""
    ast = parse(src)
    assert ast.body


def test_expression_precedence():
    src = """shuru
rakho poora x = 1 + 2 * 3
khatam
"""
    ast = parse(src)
    decl = ast.body[0]
    # should parse as 1 + (2 * 3)
    assert decl.value.op == "+"
    assert decl.value.right.op == "*"


def test_invalid_syntax_raises_error():
    with pytest.raises(ParseError):
        parse("shuru\nrakho poora x =\nkhatam\n")

