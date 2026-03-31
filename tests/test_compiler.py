from hingc.compiler.compiler import HingCCompiler


def test_compiler_success_generates_c():
    src = 'shuru\nlikho("Hi\\n")\nkhatam\n'
    res = HingCCompiler().compile(src)
    assert res.success is True
    assert res.generated_c_code is not None
    assert "int main()" in res.generated_c_code


def test_compiler_lex_error_fails_lexer_phase():
    src = "shuru\n@\nkhatam\n"
    res = HingCCompiler().compile(src)
    assert res.success is False
    assert res.phase_failed == "lexer"
    assert res.errors


def test_compiler_parse_error_fails_parser_phase():
    src = "shuru\nrakho poora x =\nkhatam\n"
    res = HingCCompiler().compile(src)
    assert res.success is False
    assert res.phase_failed == "parser"
    assert res.errors


def test_compiler_semantic_error_fails_semantic_phase():
    src = "shuru\nx = 1\nkhatam\n"
    res = HingCCompiler().compile(src)
    assert res.success is False
    assert res.phase_failed == "semantic"
    assert res.semantic_errors

