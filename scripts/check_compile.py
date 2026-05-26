from hingc.compiler.compiler import HingCCompiler

src = """shuru
rakho dasha msg = "hello"
likho("%s\\n", msg)
wapas 0
khatam
"""
res = HingCCompiler().compile(src)
print("phase_failed=", res.phase_failed)
print("errors=", [str(e) for e in res.errors])
print("semantic_errors=", [str(e) for e in res.semantic_errors])
print("generated_c_code=", bool(res.generated_c_code))
