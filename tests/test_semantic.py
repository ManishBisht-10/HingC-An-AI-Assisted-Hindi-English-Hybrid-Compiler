from hingc.compiler.parser import parse
from hingc.compiler.semantic import analyze


def test_undeclared_variable_caught():
    ast = parse("shuru\nx = 1\nkhatam\n")
    issues = analyze(ast)
    assert any("Undeclared variable 'x'" in i.message for i in issues)


def test_redeclaration_caught():
    ast = parse("shuru\nrakho poora x = 1\nrakho poora x = 2\nkhatam\n")
    issues = analyze(ast)
    assert any("Redeclaration of variable 'x'" in i.message for i in issues)


def test_type_mismatch_caught():
    ast = parse('shuru\nrakho poora x = "hi"\nkhatam\n')
    issues = analyze(ast)
    assert any("Type mismatch" in i.message for i in issues)


def test_break_outside_loop_caught():
    ast = parse("shuru\ntoro\nkhatam\n")
    issues = analyze(ast)
    assert any("outside of a loop" in i.message for i in issues)


def test_correct_program_passes():
    src = """shuru
rakho poora x = 10
rakho dasha y = 3.14
agar (x > 5) {
  likho("ok\\n")
} warna {
  likho("no\\n")
}
jabtak (x > 0) {
  x = x - 1
}
khatam
"""
    ast = parse(src)
    issues = analyze(ast)
    assert not any(i.severity == "error" for i in issues)

