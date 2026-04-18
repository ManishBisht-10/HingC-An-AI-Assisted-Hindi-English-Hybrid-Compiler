# HingC: AI-Assisted Hindi-English Hybrid Compiler

HingC is a full-stack compiler IDE for a Hindi-English hybrid programming language. It compiles HingC code through lexer, parser, semantic analysis, and C code generation, then compiles/runs the generated C with `gcc`. It also provides optional LLM-based educational explanations for compile errors.

## What This Project Includes

- HingC language compiler pipeline in Python
- FastAPI backend for compile, examples, snippets, and WebSocket compile progress
- React + Monaco frontend IDE
- Optional LLM advisor (OpenAI, Anthropic, or Ollama)
- SQLite snippet persistence via SQLAlchemy
- Dockerfiles and Docker Compose for containerized run
- Pytest test suite for compiler and API modules

## Project Structure

```text
hingc/
	api/
		main.py          # FastAPI app, REST + WebSocket endpoints
		executor.py      # Compiles generated C with gcc and executes binary
		llm_advisor.py   # LLM integration with robust fallback advice
		models.py        # SQLAlchemy models (snippets)
	compiler/
		lexer.py         # Tokenization
		parser.py        # AST construction
		semantic.py      # Type/scope checks and warnings
		codegen.py       # HingC AST -> C code generation
		compiler.py      # Orchestrates full compilation pipeline
client/
	src/
		App.jsx          # Main IDE UI
		components/      # Editor, output, errors, docs drawer, etc.
tests/               # Unit and integration tests
```

## HingC Language Snapshot

### Program Boundaries

Every program starts with `shuru` and ends with `khatam`.

```hingc
shuru
	likho("Namaste Duniya\n")
	wapas 0
khatam
```

### Supported Types

- `poora` -> `int`
- `dasha` -> `float`
- `akshar` -> `char`
- `shabd` -> `char*`
- `khaali` -> `void`

### Core Keywords

`shuru`, `khatam`, `rakho`, `agar`, `warna`, `warna agar`, `jabtak`, `karo`, `kaam`, `wapas`, `likho`, `lo`, `toro`, `agla`, `chunao`, `sthiti`, `warna_default`, `sahi`, `galat`

### Features Supported by Compiler

- Variable declarations and assignments
- Arithmetic, comparison, logical expressions
- `if` / `else if` / `else`
- `while` and `for`
- `break` and `continue`
- Function declarations and function calls
- `switch` with `case` and default
- `printf`-style output via `likho(...)`
- `scanf`-style input via `lo(...)`

### Input Syntax Note

Parser expects C-style function-call syntax for input:

```hingc
lo("%d", &x)
```

## Architecture

1. Lexer converts source into tokens.
2. Parser converts tokens to AST.
3. Semantic analyzer performs scope/type checks.
4. Code generator emits C code.
5. Executor compiles C via `gcc` and runs the binary.
6. LLM advisor (optional) provides friendly explanations and fixes.

The LLM is advisory only. Compiler correctness is determined by compiler phases, not by LLM output.

## Prerequisites

- Python 3.11+
- Node.js 18+ (or 20+ recommended)
- `gcc` available on PATH
- (Optional) Docker and Docker Compose
- (Optional) LLM provider credentials or local Ollama instance

## Quick Start (Local Development)

### 1. Backend Setup

From repository root:

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Install dependencies and start API:

```bash
pip install -r requirements.txt
uvicorn hingc.api.main:app --host 0.0.0.0 --port 8000 --reload
```

Backend URL: `http://127.0.0.1:8000`

### 2. Frontend Setup

In a new terminal:

```bash
cd client
npm install
npm run dev
```

Frontend URL (Vite): `http://127.0.0.1:5173` (or `http://localhost:5173`)

The frontend auto-detects backend URL or uses `VITE_API_URL` when provided.

## Run with Docker

From repository root:

```bash
docker-compose up --build
```

Services:

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`
- Health check: `http://localhost:8000/api/health`

Stop:

```bash
docker-compose down
```

## API Overview

### `GET /api/health`

Returns backend status and version.

### `GET /api/examples`

Returns built-in sample HingC programs.

### `POST /api/compile`

Compiles HingC source, optionally runs the resulting C program, and returns diagnostics.

Request body:

```json
{
	"source_code": "shuru\n  likho(\"Hi\\n\")\nkhatam",
	"get_llm_advice": true,
	"stdin_input": ""
}
```

Response includes:

- `success`
- `tokens`
- `ast_json`
- `semantic_errors`
- `generated_c_code`
- `errors`
- `warnings`
- `phase_failed`
- `execution`
- `llm_advice`

### `POST /api/snippets/save`

Persists a snippet in database.

```json
{
	"title": "My snippet",
	"code": "shuru\n...\nkhatam"
}
```

### `GET /api/snippets/{snippet_id}`

Fetches saved snippet by ID.

### `WS /ws/compile`

WebSocket compile endpoint that emits phase updates (`lexing`, `parsing`, etc.) and final result.

## Environment Variables

### Backend

- `MAX_CODE_LENGTH` (default: `10000`)
- `EXECUTION_TIMEOUT` (default: `10` seconds)
- `DATABASE_URL` (default: `sqlite:///./hingc.db`)
- `CORS_ORIGINS` (comma-separated origins)
- `CORS_ORIGIN_REGEX` (regex fallback)

LLM-related:

- `LLM_PROVIDER` (`ollama`, `openai`, or `anthropic`; default `ollama`)
- `LLM_MODEL` (provider model name)
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- `LLAMA_API_URL` / `OLLAMA_API_URL` (default: `http://localhost:11434`)

### Frontend

- `VITE_API_URL` (optional explicit backend URL)

## Testing

Run all tests from repository root:

```bash
pytest -q
```

Or run specific modules:

```bash
pytest tests/test_lexer.py -q
pytest tests/test_parser.py -q
pytest tests/test_semantic.py -q
pytest tests/test_codegen.py -q
pytest tests/test_api_main.py -q
```

## Common Troubleshooting

- `gcc executable not found on PATH`
	- Install GCC and ensure it is available in terminal PATH.

- WebSocket compile fails in browser
	- Frontend automatically falls back to HTTP compile endpoint.

- LLM advice missing
	- Compile still works; advisor has deterministic fallback when provider/API is unavailable.

- CORS errors
	- Configure `CORS_ORIGINS` or `CORS_ORIGIN_REGEX` for your frontend origin.

## Additional Documentation

- `QUICK_REFERENCE.md` for syntax-first language guide
- `API_DOCS.md` for detailed API examples
- `DOCKER.md` for Docker workflows
- `DEPLOYMENT.md` for deployment-oriented notes
- `CONTRIBUTING.md` for contribution workflow

## Tech Stack

- Backend: FastAPI, SQLAlchemy, Pydantic, Uvicorn
- Compiler core: Python implementation (lexer/parser/semantic/codegen)
- Frontend: React, Vite, Monaco Editor, Tailwind CSS
- Runtime execution: local `gcc`
- Testing: Pytest

## Version

Current package version: `0.1.0`

