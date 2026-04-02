from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager
from dataclasses import asdict, is_dataclass
from typing import Any, Optional
import os

from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from hingc import __version__
from hingc.api.executor import ExecutionResult, execute_c_code
from hingc.api.llm_advisor import advice_to_dict, explain_errors
from hingc.api.models import SessionLocal, Snippet, init_db
from hingc.compiler.compiler import HingCCompiler
from hingc.compiler.errors import CompilerError
from hingc.compiler.lexer import Token


EXAMPLES: list[dict[str, str]] = [
    {"name": "Hello Duniya", "code": 'shuru\nlikho("Namaste Duniya\\n")\nkhatam\n'},
    {
        "name": "Calculator",
        "code": (
            "shuru\n"
            "kaam poora jodo(poora a, poora b) {\n"
            "    wapas a + b\n"
            "}\n"
            "rakho poora x = jodo(2, 3)\n"
            "likho(\"Sum: %d\\n\", x)\n"
            "khatam\n"
        ),
    },
    {
        "name": "FizzBuzz",
        "code": (
            "shuru\n"
            "karo (rakho poora i = 1 ; i <= 15 ; i = i + 1) {\n"
            "    agar ((i % 3 == 0) aur (i % 5 == 0)) {\n"
            "        likho(\"FizzBuzz\\n\")\n"
            "    } warna agar (i % 3 == 0) {\n"
            "        likho(\"Fizz\\n\")\n"
            "    } warna agar (i % 5 == 0) {\n"
            "        likho(\"Buzz\\n\")\n"
            "    } warna {\n"
            "        likho(\"%d\\n\", i)\n"
            "    }\n"
            "}\n"
            "khatam\n"
        ),
    },
    {
        "name": "Fibonacci",
        "code": (
            "shuru\n"
            "rakho poora a = 0\n"
            "rakho poora b = 1\n"
            "rakho poora n = 7\n"
            "jabtak (n > 0) {\n"
            "    likho(\"%d \", a)\n"
            "    rakho poora next = a + b\n"
            "    a = b\n"
            "    b = next\n"
            "    n = n - 1\n"
            "}\n"
            "likho(\"\\n\")\n"
            "khatam\n"
        ),
    },
    {
        "name": "Grade Checker",
        "code": (
            "shuru\n"
            "rakho poora marks = 78\n"
            "agar (marks >= 90) {\n"
            "    likho(\"Grade A\\n\")\n"
            "} warna agar (marks >= 75) {\n"
            "    likho(\"Grade B\\n\")\n"
            "} warna agar (marks >= 60) {\n"
            "    likho(\"Grade C\\n\")\n"
            "} warna {\n"
            "    likho(\"Need improvement\\n\")\n"
            "}\n"
            "khatam\n"
        ),
    },
    {
        "name": "Simple Input",
        "code": (
            "shuru\n"
            "rakho poora x\n"
            "likho(\"Number do: \")\n"
            "lo(\"%d\", &x)\n"
            "likho(\"Aapne diya: %d\\n\", x)\n"
            "khatam\n"
        ),
    },
    {
        "name": "Broken Code",
        "code": (
            "shuru\n"
            "rakho poora x = \"hello\"\n"
            "agar (x >) {\n"
            "    likho(\"oops\\n\")\n"
            "}\n"
            "khatam\n"
        ),
    },
]


class CompileRequest(BaseModel):
    source_code: str = Field(min_length=1, max_length=int(os.getenv("MAX_CODE_LENGTH", "10000")))
    get_llm_advice: bool = True
    stdin_input: str = ""


class SnippetSaveRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    code: str = Field(min_length=1, max_length=int(os.getenv("MAX_CODE_LENGTH", "10000")))


class SnippetResponse(BaseModel):
    snippet_id: int
    title: str
    code: str


def _get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _to_jsonable(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, list):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, tuple):
        return [_to_jsonable(v) for v in value]
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v) for k, v in value.items()}
    if is_dataclass(value):
        return {k: _to_jsonable(v) for k, v in asdict(value).items()}
    return str(value)


def _serialize_error(err: CompilerError) -> dict[str, Any]:
    payload = {
        "phase": err.phase,
        "line": err.line,
        "column": err.column,
        "message": err.message,
    }
    severity = getattr(err, "severity", None)
    if severity:
        payload["severity"] = severity
    return payload


def _serialize_token(tok: Token) -> dict[str, Any]:
    return {
        "type": tok.type,
        "value": tok.value,
        "line": tok.line,
        "column": tok.column,
    }


def _serialize_execution(result: Optional[ExecutionResult]) -> Optional[dict[str, Any]]:
    if result is None:
        return None
    return {
        "success": result.success,
        "stdout": result.stdout,
        "stderr": result.stderr,
        "exit_code": result.exit_code,
        "execution_time_ms": result.execution_time_ms,
        "timed_out": result.timed_out,
        "gcc_error": result.gcc_error,
    }


async def _compile_flow(req: CompileRequest) -> dict[str, Any]:
    compiler = HingCCompiler()
    result = compiler.compile(req.source_code)

    execution: Optional[ExecutionResult] = None
    if result.success and result.generated_c_code:
        timeout = int(os.getenv("EXECUTION_TIMEOUT", "10"))
        execution = await execute_c_code(
            c_code=result.generated_c_code,
            stdin_input=req.stdin_input,
            timeout=timeout,
        )

    llm_advice = None
    if req.get_llm_advice:
        llm = await explain_errors(
            source_code=req.source_code,
            errors=result.errors,
            generated_c=result.generated_c_code,
        )
        llm_advice = advice_to_dict(llm)

    return {
        "success": result.success,
        "tokens": [_serialize_token(tok) for tok in result.tokens],
        "ast_json": _to_jsonable(result.ast),
        "semantic_errors": [_serialize_error(err) for err in result.semantic_errors],
        "generated_c_code": result.generated_c_code,
        "errors": [_serialize_error(err) for err in result.errors],
        "warnings": list(result.warnings),
        "phase_failed": result.phase_failed,
        "execution": _serialize_execution(execution),
        "llm_advice": llm_advice,
    }


def _parse_cors_origins() -> list[str]:
    default_origins = ",".join(
        [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000",
        ]
    )
    raw = os.getenv("CORS_ORIGINS", default_origins)
    return [item.strip() for item in raw.split(",") if item.strip()]


def _cors_origin_regex() -> str:
    # Allow local-network dev URLs like http://10.x.x.x:5173, http://172.x.x.x:5173, http://192.168.x.x:5173
    return os.getenv("CORS_ORIGIN_REGEX", r"^https?://(localhost|127\.0\.0\.1|(?:\d{1,3}\.){3}\d{1,3})(:\d+)?$")


@asynccontextmanager
async def _lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="HingC API", version=__version__, lifespan=_lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(),
    allow_origin_regex=_cors_origin_regex(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": __version__}


@app.get("/api/examples")
async def list_examples() -> list[dict[str, str]]:
    return EXAMPLES


@app.post("/api/compile")
async def compile_endpoint(req: CompileRequest) -> dict[str, Any]:
    return await _compile_flow(req)


@app.post("/api/snippets/save", response_model=SnippetResponse)
async def save_snippet(req: SnippetSaveRequest, db: Session = Depends(_get_db)) -> SnippetResponse:
    row = Snippet(title=req.title, code=req.code)
    db.add(row)
    db.commit()
    db.refresh(row)
    return SnippetResponse(snippet_id=row.id, title=row.title, code=row.code)


@app.get("/api/snippets/{snippet_id}", response_model=SnippetResponse)
async def get_snippet(snippet_id: int, db: Session = Depends(_get_db)) -> SnippetResponse:
    row = db.get(Snippet, snippet_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Snippet not found")
    return SnippetResponse(snippet_id=row.id, title=row.title, code=row.code)


@app.websocket("/ws/compile")
async def ws_compile(websocket: WebSocket) -> None:
    await websocket.accept()
    try:
        while True:
            payload = await websocket.receive_json()
            req = CompileRequest(**payload)

            for phase in ("lexing...", "parsing...", "analyzing...", "generating C..."):
                await websocket.send_json({"event": "phase", "message": phase})
                await asyncio.sleep(0)

            response = await _compile_flow(req)

            if response.get("success"):
                await websocket.send_json({"event": "phase", "message": "compiling C..."})
                await asyncio.sleep(0)
                await websocket.send_json({"event": "phase", "message": "running..."})
                await asyncio.sleep(0)

            await websocket.send_json({"event": "done", "result": response})
    except WebSocketDisconnect:
        return
