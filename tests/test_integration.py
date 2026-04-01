import pytest
import requests
from hingc.compiler import tokenize, Parser, compile_to_c
from hingc.api.executor import execute_c_code
import json
import time

# Integration tests that test the full compilation pipeline

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 10

class TestCompilationPipeline:
    """Test end-to-end compilation from HingC to C to execution"""

    @pytest.fixture
    def sample_program(self):
        return """shuru
  rakho poora x = 10
  rakho poora y = 5
  rakho poora sum = x + y
  likho("Sum: %d\\n", sum)
  wapas 0
khatam"""

    @pytest.fixture
    def loop_program(self):
        return """shuru
  karo (rakho poora i = 1; i <= 3; i = i + 1) {
    likho("i=%d\\n", i)
  }
  wapas 0
khatam"""

    def test_api_health(self):
        """Test API health endpoint"""
        resp = requests.get(f"{BASE_URL}/api/health", timeout=TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"

    def test_compile_simple_program(self, sample_program):
        """Test compilation of simple program"""
        payload = {
            "source_code": sample_program,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["errors"]) == 0
        assert "generated_c_code" in data
        assert len(data["generated_c_code"]) > 0

    def test_compile_with_errors(self):
        """Test compilation of program with errors"""
        bad_program = "shuru rakho x = invalid khatam"
        payload = {
            "source_code": bad_program,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["errors"]) > 0

    def test_keywords_tokenization(self):
        """Test that all keywords are properly tokenized"""
        code = """shuru
  rakho poora x = 10
  agar (x > 5) { likho("yes\\n") } warna { likho("no\\n") }
  jabtak (x > 0) { x = x - 1 }
  karo (rakho poora i = 0; i < 3; i = i + 1) { likho("i\\n") }
  chunao (x) { sthiti 1: likho("case\\n") toro warna_default: likho("def\\n") }
  wapas 0
khatam"""
        tokens = tokenize(code)
        keyword_tokens = [t for t in tokens if t.type == "keyword"]
        keyword_values = set(t.value for t in keyword_tokens)
        
        expected = {
            "shuru", "rakho", "poora", "agar", "warna", "jabtak",
            "karo", "chunao", "sthiti", "warna_default", "toro", "wapas", "khatam"
        }
        assert expected.issubset(keyword_values)

    def test_parser_creates_ast(self):
        """Test that parser creates valid AST"""
        code = """shuru
  rakho poora x = 10
  wapas x
khatam"""
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        assert ast is not None
        assert len(ast.body) > 0

    def test_code_generation(self):
        """Test C code generation from AST"""
        code = """shuru
  rakho poora result = 42
  likho("Result: %d\\n", result)
  wapas 0
khatam"""
        tokens = tokenize(code)
        parser = Parser(tokens)
        ast = parser.parse()
        c_code = compile_to_c(ast, tokens)
        
        assert c_code is not None
        assert "#include" in c_code
        assert "int main" in c_code
        assert "printf" in c_code

    def test_api_examples_endpoint(self):
        """Test examples API endpoint"""
        resp = requests.get(f"{BASE_URL}/api/examples", timeout=TIMEOUT)
        assert resp.status_code == 200
        data = resp.json()
        assert "examples" in data
        assert len(data["examples"]) > 0

    def test_full_compilation_flow(self, sample_program):
        """Test full compilation flow without errors"""
        payload = {
            "source_code": sample_program,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        assert resp.status_code == 200
        data = resp.json()

        # Check compilation phases
        assert "tokens" in data
        assert "ast_json" in data
        assert "generated_c_code" in data
        assert "errors" in data
        assert len(data["errors"]) == 0

        # Check AST structure
        ast = data.get("ast_json")
        assert ast is not None

        # Check tokens
        tokens = data.get("tokens", [])
        assert len(tokens) > 0


class TestErrorHandling:
    """Test error detection and reporting"""

    def test_syntax_error_detection(self):
        """Test detection of syntax errors"""
        bad_code = "shuru rakho x = invalid_literal khatam"
        payload = {
            "source_code": bad_code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) > 0
        error = data["errors"][0]
        assert error["phase"] in ["lexer", "parser", "semantic"]

    def test_undefined_variable_error(self):
        """Test detection of undefined variable"""
        code = """shuru
  likho("Value: %d\\n", undefined_var)
  wapas 0
khatam"""
        payload = {
            "source_code": code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) > 0

    def test_missing_program_boundaries(self):
        """Test error on missing shuru/khatam"""
        code = "likho(\"hello\\n\")"
        payload = {
            "source_code": code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) > 0


class TestTypes:
    """Test type system"""

    def test_integer_type(self):
        """Test integer type declaration"""
        code = """shuru
  rakho poora x = 42
  likho("%d\\n", x)
  wapas 0
khatam"""
        payload = {
            "source_code": code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) == 0

    def test_string_type(self):
        """Test string type declaration"""
        code = """shuru
  rakho dasha msg = "hello"
  likho("%s\\n", msg)
  wapas 0
khatam"""
        payload = {
            "source_code": code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) == 0

    def test_character_type(self):
        """Test character type declaration"""
        code = """shuru
  rakho akshar c = 'A'
  wapas 0
khatam"""
        payload = {
            "source_code": code,
            "get_llm_advice": False,
            "stdin_input": "",
        }
        resp = requests.post(
            f"{BASE_URL}/api/compile",
            json=payload,
            timeout=TIMEOUT,
        )
        data = resp.json()
        assert len(data["errors"]) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
