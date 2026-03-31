import pytest

from hingc.compiler.errors import LexerError
from hingc.compiler.lexer import lex


def types_values(tokens):
    return [(t.type, t.value) for t in tokens]


def test_keywords_tokenized_correctly():
    src = "shuru\nkhatam\n"
    tv = types_values(lex(src))
    assert ("KEYWORD", "shuru") in tv
    assert ("KEYWORD", "khatam") in tv


def test_identifier_vs_keyword():
    src = "rakho poora agarX = 1\n"
    tv = types_values(lex(src))
    assert ("KEYWORD", "rakho") in tv
    assert ("KEYWORD", "poora") in tv
    assert ("IDENTIFIER", "agarX") in tv


def test_number_literals_int_and_float():
    src = "rakho poora x = 10\nrakho dasha pi = 3.14\n"
    tv = types_values(lex(src))
    assert ("NUMBER_INT", "10") in tv
    assert ("NUMBER_FLOAT", "3.14") in tv


def test_string_literals():
    src = 'likho("Namaste\\n")\n'
    toks = lex(src)
    s = next(t for t in toks if t.type == "STRING_LITERAL")
    assert s.value == "Namaste\n"


def test_multiline_program_and_newlines():
    src = "shuru\nrakho poora x = 5\nkhatam\n"
    toks = lex(src)
    assert toks[0].type == "KEYWORD"
    assert sum(1 for t in toks if t.type == "NEWLINE") == 3
    assert toks[-1].type == "EOF"


def test_invalid_character_raises_error():
    with pytest.raises(LexerError) as e:
        lex("rakho poora x = 1 @\n")
    assert "Invalid character" in str(e.value)


def test_comment_skipped():
    src = "rakho poora x = 1 // comment\nrakho poora y = 2\n"
    tv = types_values(lex(src))
    assert ("IDENTIFIER", "x") in tv
    assert ("IDENTIFIER", "y") in tv
    # No COMMENT tokens emitted in this lexer design
    assert not any(t == ("COMMENT", "//") for t in tv)


def test_multiword_keyword_warna_agar():
    src = "warna agar (x == 1) {\n}\n"
    tv = types_values(lex(src))
    assert ("KEYWORD", "warna agar") in tv

