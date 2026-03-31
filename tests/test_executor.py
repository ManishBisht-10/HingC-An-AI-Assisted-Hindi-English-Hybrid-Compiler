import asyncio
import shutil

import pytest

from hingc.api.executor import execute_c_code


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc not available on PATH")
def test_execute_c_code_runs_and_captures_stdout():
    c = r"""
#include <stdio.h>
int main() {
  printf("Hello\n");
  return 0;
}
"""
    res = asyncio.run(execute_c_code(c, timeout=5))
    if (not res.success) and ("blocked" in res.stderr.lower() or "policy" in res.stderr.lower()):
        pytest.skip(f"Execution blocked by OS policy: {res.stderr}")
    assert res.gcc_error is None
    assert res.timed_out is False
    assert res.stdout.replace("\r\n", "\n") == "Hello\n"


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc not available on PATH")
def test_execute_c_code_stdin():
    c = r"""
#include <stdio.h>
int main() {
  int x = 0;
  if (scanf("%d", &x) != 1) return 2;
  printf("%d\n", x + 1);
  return 0;
}
"""
    res = asyncio.run(execute_c_code(c, stdin_input="41\n", timeout=5))
    if (not res.success) and ("blocked" in res.stderr.lower() or "policy" in res.stderr.lower()):
        pytest.skip(f"Execution blocked by OS policy: {res.stderr}")
    assert res.stdout.strip() == "42"

