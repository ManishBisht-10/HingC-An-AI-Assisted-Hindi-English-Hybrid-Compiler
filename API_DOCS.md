# HingC API Documentation

Complete reference for all HingC backend API endpoints.

## Base URL

**Development:** `http://127.0.0.1:8000`
**Production:** `https://api.hingc.example.com`

All responses are in JSON format.

## Authentication

Currently, the API is public. Future versions will support:
- API keys
- OAuth 2.0
- JWT tokens

For now, include standard headers:
```
Content-Type: application/json
```

## Response Format

All successful responses follow this structure:

```json
{
  "status": "success",
  "data": { ... },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "version": "1.0"
  }
}
```

Error responses:

```json
{
  "status": "error",
  "error": {
    "code": "COMPILE_ERROR",
    "message": "Syntax error at line 5",
    "phase": "parser"
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

## Endpoints

### 1. Health Check

#### GET `/api/health`

Check if the API is running and healthy.

**Response:**
```json
{
  "status": "success",
  "data": {
    "status": "ok",
    "uptime_seconds": 3600,
    "version": "1.0.0"
  }
}
```

**Status Codes:**
- `200` - API is healthy
- `503` - API is unhealthy

---

### 2. Compile Code

#### POST `/api/compile`

Compile HingC code to C and execute.

**Request Body:**
```json
{
  "source_code": "shuru\n  rakho poora x = 10\n  likho(\"Value: %d\\n\", x)\n  wapas 0\nkhatam",
  "get_llm_advice": true,
  "stdin_input": "",
  "timeout_seconds": 5
}
```

**Query Parameters:**
- `get_llm_advice` (bool): Include LLM-generated error explanations (default: `false`)
- `timeout_seconds` (int): Execution timeout (default: `5`)

**Request Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `source_code` | string | Yes | HingC source code (max 100KB) |
| `get_llm_advice` | boolean | No | Request AI-powered error explanations |
| `stdin_input` | string | No | Standard input for program execution |
| `timeout_seconds` | integer | No | Execution timeout (1-30 seconds) |

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "tokens": [
      {
        "type": "KEYWORD",
        "value": "shuru",
        "line": 1,
        "column": 1
      },
      {
        "type": "KEYWORD",
        "value": "rakho",
        "line": 2,
        "column": 3
      }
    ],
    "ast_json": {
      "type": "Program",
      "body": [
        {
          "type": "Declaration",
          "name": "x",
          "dataType": "poora",
          "value": 10
        }
      ]
    },
    "generated_c_code": "#include <stdio.h>\n#include <string.h>\n\nint main() {\n  int x = 10;\n  printf(\"Value: %d\\n\", x);\n  return 0;\n}",
    "execution": {
      "stdout": "Value: 10\n",
      "stderr": "",
      "execution_time_ms": 15.5,
      "exit_code": 0,
      "status": "completed"
    },
    "errors": [],
    "llm_advice": null,
    "compilation_time_ms": 45.2,
    "total_time_ms": 60.7
  },
  "meta": {
    "timestamp": "2024-01-15T10:30:00Z",
    "compiler_version": "1.0"
  }
}
```

**Response (Compilation Error):**
```json
{
  "status": "success",
  "data": {
    "tokens": [],
    "ast_json": null,
    "generated_c_code": null,
    "execution": null,
    "errors": [
      {
        "type": "SyntaxError",
        "phase": "parser",
        "message": "Expected 'agar' or 'khatam', got 'IDENTIFIER'",
        "line": 3,
        "column": 5,
        "snippet": "  undefined_keyword x",
        "severity": "error"
      }
    ],
    "llm_advice": {
      "explanation": "It looks like you're using a keyword that doesn't exist in HingC...",
      "suggestion": "Did you mean 'rakho' (to declare a variable)?",
      "code_fix": "rakho poora x = 5"
    },
    "compilation_time_ms": 5.2
  }
}
```

**Response (Runtime Error):**
```json
{
  "status": "success",
  "data": {
    "tokens": [...],
    "ast_json": {...},
    "generated_c_code": "...",
    "execution": {
      "stdout": "",
      "stderr": "Segmentation fault",
      "exit_code": 139,
      "status": "crashed",
      "timeout": false,
      "execution_time_ms": 125.5
    },
    "errors": [
      {
        "type": "RuntimeError",
        "phase": "executor",
        "message": "Program crashed with signal SIGSEGV",
        "severity": "error"
      }
    ],
    "compilation_time_ms": 8.5
  }
}
```

**Status Codes:**
- `200` - Compilation successful (may include errors)
- `400` - Invalid request
- `408` - Execution timeout
- `413` - Source code too large
- `500` - Server error

**Error Codes:**
- `LEXER_ERROR` - Tokenization failed
- `PARSER_ERROR` - Syntax error
- `SEMANTIC_ERROR` - Type or scope error
- `CODEGEN_ERROR` - Code generation failed
- `EXECUTOR_ERROR` - Compilation or execution failed
- `TIMEOUT_ERROR` - Execution exceeded timeout
- `VALIDATION_ERROR` - Input validation failed

---

### 3. Get Examples

#### GET `/api/examples`

Retrieve available HingC example programs.

**Query Parameters:**
- `category` (string): Filter by category (optional)
- `limit` (int): Maximum results (default: 50)

**Response:**
```json
{
  "status": "success",
  "data": {
    "examples": [
      {
        "id": "hello_world",
        "name": "Hello World",
        "category": "basics",
        "description": "Simple Hello World program",
        "code": "shuru\n  likho(\"Hello, World!\\n\")\n  wapas 0\nkhatam",
        "difficulty": "easy",
        "tags": ["hello", "output"],
        "expected_output": "Hello, World!\n"
      },
      {
        "id": "variables",
        "name": "Variables",
        "category": "basics",
        "description": "Declaring and using variables",
        "code": "shuru\n  rakho poora x = 10\n  rakho poora y = 20\n  rakho poora sum = x + y\n  likho(\"%d\\n\", sum)\n  wapas 0\nkhatam",
        "difficulty": "easy",
        "tags": ["variables", "arithmetic"],
        "expected_output": "30\n"
      }
    ],
    "total": 10,
    "categories": ["basics", "control_flow", "functions", "advanced"]
  }
}
```

**Status Codes:**
- `200` - Success
- `404` - Category not found

---

### 4. Get Language Reference

#### GET `/api/reference`

Get HingC language reference (keywords, operators, types).

**Response:**
```json
{
  "status": "success",
  "data": {
    "keywords": [
      {
        "keyword": "shuru",
        "meaning": "Start program",
        "syntax": "shuru",
        "example": "shuru",
        "category": "program_structure"
      },
      {
        "keyword": "rakho",
        "meaning": "Declare variable",
        "syntax": "rakho [type] [name] = [value]",
        "example": "rakho poora x = 10",
        "category": "variables"
      }
    ],
    "types": [
      {
        "type": "poora",
        "meaning": "Integer",
        "c_equivalent": "int",
        "range": "-2147483648 to 2147483647"
      },
      {
        "type": "dasha",
        "meaning": "String",
        "c_equivalent": "char*",
        "example": "rakho dasha msg = \"Hi\""
      },
      {
        "type": "akshar",
        "meaning": "Character",
        "c_equivalent": "char",
        "example": "rakho akshar c = 'a'"
      }
    ],
    "operators": [
      {
        "operator": "aur",
        "meaning": "Logical AND",
        "c_equivalent": "&&",
        "example": "agar (x > 5 aur y < 10)"
      },
      {
        "operator": "ya",
        "meaning": "Logical OR",
        "c_equivalent": "||",
        "example": "agar (x > 5 ya y < 10)"
      }
    ]
  }
}
```

---

### 5. Save Code Snippet

#### POST `/api/snippets/save`

Save a code snippet for future reference.

**Request Body:**
```json
{
  "title": "My First Program",
  "code": "shuru\n  likho(\"Hello\\n\")\n  wapas 0\nkhatam",
  "description": "A simple hello program",
  "tags": ["hello", "beginner"],
  "is_public": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": "snippet_123",
    "title": "My First Program",
    "code": "shuru\n  likho(\"Hello\\n\")\n  wapas 0\nkhatam",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "url": "https://hingc.example.com/snippets/snippet_123"
  }
}
```

**Status Codes:**
- `201` - Snippet created
- `400` - Invalid request
- `500` - Server error

---

### 6. Get Saved Snippets

#### GET `/api/snippets`

Retrieve saved code snippets.

**Query Parameters:**
- `limit` (int): Maximum results (default: 20)
- `offset` (int): Pagination offset (default: 0)
- `tag` (string): Filter by tag

**Response:**
```json
{
  "status": "success",
  "data": {
    "snippets": [
      {
        "id": "snippet_123",
        "title": "My First Program",
        "description": "A simple hello program",
        "code": "shuru\n  likho(\"Hello\\n\")\n  wapas 0\nkhatam",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z",
        "tags": ["hello", "beginner"]
      }
    ],
    "total": 1,
    "limit": 20,
    "offset": 0
  }
}
```

---

### 7. WebSocket: Stream Compilation

#### WS `/ws/compile`

WebSocket endpoint for real-time compilation streaming.

**Connection:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/compile');

ws.onopen = () => {
  ws.send(JSON.stringify({
    source_code: "shuru likho(\"test\\n\") khatam",
    get_llm_advice: true
  }));
};

ws.onmessage = (event) => {
  const update = JSON.parse(event.data);
  console.log(update);
  // Handle: tokens, ast, codegen, execution updates
};

ws.onerror = (error) => {
  console.error("WebSocket error:", error);
};
```

**Message Format:**
```json
{
  "type": "tokens",
  "phase": "lexer",
  "data": [{...}],
  "progress": 25
}
```

**Message Types:**
- `tokens` - Lexer phase complete
- `ast` - Parser phase complete
- `codegen` - Code generation complete
- `execution` - Program execution complete
- `error` - Error occurred
- `progress` - Progress update

---

## Rate Limiting

Default rate limits:
- **Unauthenticated:** 10 requests per minute
- **Authenticated:** 100 requests per minute
- **Batch compilation:** 2 per minute

Rate limit headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1705315800
```

---

## Error Handling

### Common Error Codes

| Code | Status | Description |
|------|--------|-------------|
| `INVALID_REQUEST` | 400 | Malformed request |
| `SOURCE_TOO_LARGE` | 413 | Source code exceeds limit |
| `TIMEOUT` | 408 | Execution timeout |
| `INTERNAL_ERROR` | 500 | Server error |

### Example Error Response

```json
{
  "status": "error",
  "error": {
    "code": "COMPILER_ERROR",
    "message": "Syntax error: unexpected token 'IDENTIFIER'",
    "phase": "parser",
    "line": 3,
    "column": 5,
    "details": {
      "expected": ["keyword", "operator"],
      "got": "IDENTIFIER"
    }
  }
}
```

---

## Pagination

Endpoints supporting large result sets use pagination:

```
GET /api/snippets?limit=20&offset=40
```

Response includes:
```json
{
  "data": [...],
  "pagination": {
    "limit": 20,
    "offset": 40,
    "total": 150
  }
}
```

---

## Testing API with cURL

```bash
# Health check
curl http://localhost:8000/api/health

# Compile simple program
curl -X POST http://localhost:8000/api/compile \
  -H "Content-Type: application/json" \
  -d '{
    "source_code": "shuru likho(\"Hello\\n\") wapas 0 khatam",
    "get_llm_advice": false
  }'

# Get examples
curl http://localhost:8000/api/examples

# Get language reference
curl http://localhost:8000/api/reference
```

---

## Testing API with Python

```python
import requests

# Compile code
response = requests.post(
    'http://localhost:8000/api/compile',
    json={
        'source_code': 'shuru likho("Hello\\n") wapas 0 khatam',
        'get_llm_advice': True
    }
)

result = response.json()
print(f"Status: {result['status']}")
print(f"Generated C:\n{result['data']['generated_c_code']}")
print(f"Output: {result['data']['execution']['stdout']}")
```

---

## API Changelog

### v1.0 (Current)
- Initial release
- Core compilation endpoints
- WebSocket support
- Example programs
- Language reference

---

## Support

For issues or questions:
- GitHub Issues: [Report bugs](https://github.com/hingc/issues)
- Documentation: [Read docs](README.md)
- Discussions: [Ask questions](https://github.com/hingc/discussions)

---

**Last Updated:** 2024-01-15
**API Version:** 1.0
