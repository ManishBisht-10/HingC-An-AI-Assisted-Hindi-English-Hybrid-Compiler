# Contributing to HingC

We welcome contributions to the HingC compiler project! This guide will help you get started.

## Code of Conduct

We are committed to providing a welcoming and inspiring community. Please read our [Code of Conduct](CODE_OF_CONDUCT.md).

## How to Contribute

### 1. Report Issues

Found a bug? Have a feature request? Please open an issue on GitHub with:
- **Clear description** of the problem or feature
- **Steps to reproduce** (for bugs)
- **Expected vs actual behavior**
- **Environment** (OS, Python version, etc.)

### 2. Write Code

#### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/username/HingC-An-AI-Assisted-Hindi-English-Hybrid-Compiler.git
cd HingC-An-AI-Assisted-Hindi-English-Hybrid-Compiler

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### Development Workflow

1. Create a feature branch:
```bash
git checkout -b feature/my-feature
```

2. Make changes and commit:
```bash
git add .
git commit -m "Add my feature"
```

3. Run tests:
```bash
pytest tests/ -v --cov=hingc
```

4. Push and create pull request:
```bash
git push origin feature/my-feature
```

### 3. Add New Keywords

Adding a new keyword to HingC involves updates to:

#### 1. Lexer (`hingc/compiler/lexer.py`)
```python
KEYWORDS = {
    'new_keyword': 'NEW_KEYWORD_TOKEN',
    # ... existing keywords
}
```

#### 2. Parser (`hingc/compiler/parser.py`)
```python
def parse_new_keyword_statement(self):
    self.consume('NEW_KEYWORD_TOKEN')
    # parsing logic
    return NewKeywordNode(...)
```

#### 3. AST Node (`hingc/compiler/ast_nodes.py`)
```python
class NewKeywordNode(ASTNode):
    def __init__(self, ...):
        self.field1 = ...
```

#### 4. Semantic Analyzer (`hingc/compiler/semantic.py`)
```python
def visit_NewKeywordNode(self, node):
    # type checking and validation
    return validated_node
```

#### 5. Code Generator (`hingc/compiler/codegen.py`)
```python
def visit_NewKeywordNode(self, node):
    c_code = "// C code for new keyword\n"
    return c_code
```

#### 6. Tests (`tests/`)
```python
# test_lexer.py
def test_new_keyword_tokenization():
    tokens = tokenize("new_keyword x")
    assert tokens[0].type == 'NEW_KEYWORD_TOKEN'

# test_parser.py
def test_new_keyword_parsing():
    ast = parse("shuru\n  new_keyword x\nkhatam")
    assert isinstance(ast.body[0], NewKeywordNode)

# test_codegen.py
def test_new_keyword_codegen():
    c_code = generate_c("shuru\n  new_keyword x\nkhatam")
    assert "// new keyword" in c_code
```

#### 7. Examples (`client/src/lib/examples.js`)
```javascript
{
  name: "Using New Keyword",
  code: "shuru\n  new_keyword x\nkhatam"
}
```

#### 8. HingC Language Definition (`client/src/lib/hingcLanguage.js`)
Add to Monarch tokenizer configuration.

### 4. Add Frontend Component

#### Example: Adding a new panel

1. Create component:
```jsx
// client/src/components/MyPanel.jsx
export const MyPanel = ({ data }) => {
  return (
    <div className="p-4 bg-white rounded">
      {/* Component content */}
    </div>
  );
};
```

2. Import in App.jsx:
```jsx
import { MyPanel } from './components/MyPanel';

export const App = () => {
  return (
    <>
      <MyPanel data={data} />
    </>
  );
};
```

3. Style with Tailwind:
```jsx
<div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
  <div className="bg-gray-50 rounded-lg p-4">
    {/* Panel content */}
  </div>
</div>
```

### 5. Add Tests

#### Unit Test Example
```python
import pytest
from hingc.compiler.lexer import tokenize

def test_my_feature():
    """Test description"""
    result = my_function()
    assert result == expected_value

def test_my_feature_edge_case():
    """Test edge case"""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

#### Integration Test Example
```python
import requests

def test_compilation_with_new_feature():
    response = requests.post(
        'http://127.0.0.1:8000/api/compile',
        json={'source_code': 'shuru ... khatam'}
    )
    assert response.status_code == 200
    assert 'generated_c_code' in response.json()
```

## Style Guide

### Python

Follow PEP 8:
```bash
# Format code
black hingc/

# Check style
flake8 hingc/ --max-line-length=100

# Type hints
from typing import List, Dict, Optional

def process_tokens(tokens: List[str]) -> Dict[str, int]:
    pass
```

### JavaScript/JSX

Follow Prettier:
```bash
# Format code
npx prettier --write client/src

# ESLint
npx eslint client/src
```

### Comments

```python
# Good: Explain WHY, not WHAT
def tokenize(source: str) -> List[Token]:
    # Skip whitespace to focus on meaningful tokens
    tokens = []
    for char in source:
        if not char.isspace():
            tokens.append(...)
    return tokens

# Avoid: Obvious comments
# Increment i
i = i + 1
```

## Documentation

- Update docstrings with changes:
```python
def my_function(param: str) -> str:
    """
    Brief description.
    
    Args:
        param: Description of parameter
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
    pass
```

- Update README.md if adding features
- Update DEPLOYMENT.md if changing deployment
- Add comments to complex algorithms

## Testing Requirements

- All changes must include tests
- Minimum 80% code coverage
- All existing tests must pass

```bash
# Run with coverage
pytest tests/ --cov=hingc --cov-report=html
```

## Pull Request Process

1. Ensure all tests pass: `pytest tests/ -v`
2. Ensure code is formatted: `black hingc/`, `npx prettier --write client/src`
3. Ensure no linting errors: `flake8 hingc/`, `npx eslint client/src`
4. Create descriptive PR with context
5. Link related issues
6. Respond to review feedback
7. Request re-review after changes

## Commit Messages

Use clear, descriptive commit messages:

```
feat: add new keyword to compiler
- Implement lexer tokenization
- Update parser rules
- Add semantic validation
- Generate C code

fix: handle edge case in parser
docs: update deployment guide
test: add integration test for keyword
```

## Performance Guidelines

- Lexer should handle files < 1MB in < 100ms
- AST generation < 50ms
- Code generation < 50ms
- C compilation < 1s
- Execution should return within 5s timeout

Benchmark your changes:
```bash
python -m timeit -s "from hingc import compile_code" \
  "compile_code('shuru likho(\"test\\\\n\") khatam')"
```

## Security

- Never commit secrets (API keys, passwords)
- Input validation for all user data
- Sanitize error messages in frontend
- SQL injection prevention (use parameterized queries)
- Rate limiting on API endpoints

## Review Criteria

PRs are reviewed on:
- ✅ All tests passing
- ✅ Code coverage maintained
- ✅ Follows style guide
- ✅ Solves stated problem
- ✅ No breaking changes
- ✅ Documentation updated
- ✅ Clear commit messages

## Resources

- [Compiler Design](#) - Background reading
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [React Docs](https://react.dev/)
- [Python PEP 8](https://pep8.org/)

## Questions?

- Open an issue on GitHub
- Ask in discussions
- Check existing issues

Thank you for contributing! 🎉
