from __future__ import annotations

import asyncio
import os
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass(frozen=True, slots=True)
class ExecutionResult:
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: float
    timed_out: bool
    gcc_error: Optional[str]


async def execute_c_code(c_code: str, stdin_input: Optional[str] = None, timeout: int = 10) -> ExecutionResult:
    """
    Compile and execute generated C code using local gcc.

    Note: Docker sandboxing is added in a later step; this is a local executor.
    """

    t0 = time.perf_counter()
    tmp_dir = Path(os.environ.get("TEMP", "")) if os.name == "nt" else Path("/tmp")
    tmp_dir.mkdir(parents=True, exist_ok=True)

    run_id = uuid.uuid4().hex
    c_path = tmp_dir / f"hingc_{run_id}.c"
    exe_path = tmp_dir / (f"hingc_{run_id}.exe" if os.name == "nt" else f"hingc_{run_id}")

    try:
        c_path.write_text(c_code, encoding="utf-8")

        # 1) compile
        try:
            gcc = await asyncio.create_subprocess_exec(
                "gcc",
                str(c_path),
                "-o",
                str(exe_path),
                "-w",
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except FileNotFoundError:
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="gcc executable not found on PATH",
                exit_code=-1,
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
                timed_out=False,
                gcc_error="gcc executable not found on PATH",
            )
        gcc_out, gcc_err = await gcc.communicate()
        if gcc.returncode != 0:
            return ExecutionResult(
                success=False,
                stdout=(gcc_out or b"").decode("utf-8", errors="replace"),
                stderr="",
                exit_code=gcc.returncode or 1,
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
                timed_out=False,
                gcc_error=(gcc_err or b"").decode("utf-8", errors="replace"),
            )

        # 2) run
        try:
            proc = await asyncio.create_subprocess_exec(
                str(exe_path),
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
        except OSError as e:
            # Common on locked-down Windows environments (Application Control / WDAC):
            # execution of a newly created temp .exe may be blocked.
            return ExecutionResult(
                success=False,
                stdout="",
                stderr=str(e),
                exit_code=-1,
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
                timed_out=False,
                gcc_error=None,
            )
        try:
            out_b, err_b = await asyncio.wait_for(
                proc.communicate(input=(stdin_input or "").encode("utf-8")),
                timeout=timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            return ExecutionResult(
                success=False,
                stdout="",
                stderr="Execution timed out",
                exit_code=-1,
                execution_time_ms=(time.perf_counter() - t0) * 1000.0,
                timed_out=True,
                gcc_error=None,
            )

        return ExecutionResult(
            success=(proc.returncode == 0),
            stdout=(out_b or b"").decode("utf-8", errors="replace"),
            stderr=(err_b or b"").decode("utf-8", errors="replace"),
            exit_code=int(proc.returncode or 0),
            execution_time_ms=(time.perf_counter() - t0) * 1000.0,
            timed_out=False,
            gcc_error=None,
        )
    finally:
        # cleanup best-effort
        try:
            if c_path.exists():
                c_path.unlink()
        except OSError:
            pass
        try:
            if exe_path.exists():
                exe_path.unlink()
        except OSError:
            pass

