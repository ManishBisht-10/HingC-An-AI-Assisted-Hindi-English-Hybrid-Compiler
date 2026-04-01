import { useEffect, useMemo, useState, useRef } from "react";
import Editor from "./components/Editor";
import OutputPanel from "./components/OutputPanel";
import ErrorPanel from "./components/ErrorPanel";
import AiAdvisor from "./components/AiAdvisor";
import ExamplesDropdown from "./components/ExamplesDropdown";
import ExamplesDocDrawer from "./components/ExamplesDocDrawer";
import { compileSource, fetchExamples, getWsUrl, saveSnippet } from "./lib/api";
import { DEFAULT_PROGRAM } from "./lib/defaultProgram";

const initialStatus = {
  phase: "idle",
  running: false,
};

export default function App() {
  const editorRef = useRef(null);
  const [sourceCode, setSourceCode] = useState(DEFAULT_PROGRAM);
  const [stdinInput, setStdinInput] = useState("");
  const [examples, setExamples] = useState([]);
  const [status, setStatus] = useState(initialStatus);
  const [compileResult, setCompileResult] = useState(null);
  const [activeTab, setActiveTab] = useState("Output");
  const [loadingAdvice, setLoadingAdvice] = useState(false);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    fetchExamples().then(setExamples).catch((error) => {
      setErrorMessage(error.message);
    });
  }, []);

  const markers = useMemo(() => {
    if (!compileResult) {
      return [];
    }

    const errorMarkers = (compileResult.errors || []).map((item) => ({
      startLineNumber: item.line || 1,
      endLineNumber: item.line || 1,
      startColumn: item.column || 1,
      endColumn: (item.column || 1) + 1,
      message: item.message,
      severity: 8,
    }));

    const warningMarkers = (compileResult.warnings || []).map((warning, idx) => ({
      startLineNumber: 1 + idx,
      endLineNumber: 1 + idx,
      startColumn: 1,
      endColumn: 2,
      message: warning,
      severity: 4,
    }));

    return [...errorMarkers, ...warningMarkers];
  }, [compileResult]);

  async function runCompilation() {
    setStatus({ running: true, phase: "starting..." });
    setErrorMessage("");

    const ws = new WebSocket(getWsUrl());
    let finished = false;

    ws.onopen = () => {
      ws.send(
        JSON.stringify({
          source_code: sourceCode,
          get_llm_advice: true,
          stdin_input: stdinInput,
        }),
      );
    };

    ws.onmessage = (event) => {
      const payload = JSON.parse(event.data);
      if (payload.event === "phase") {
        setStatus({ running: true, phase: payload.message });
        if (payload.message === "generating C...") {
          setLoadingAdvice(true);
        }
        return;
      }

      if (payload.event === "done") {
        finished = true;
        setCompileResult(payload.result);
        setLoadingAdvice(false);
        setStatus({ running: false, phase: "done" });
        ws.close();
      }
    };

    ws.onerror = () => {
      if (finished) {
        return;
      }

      finished = true;
      setStatus(initialStatus);
      setLoadingAdvice(false);
      setErrorMessage("WebSocket compile failed. Trying HTTP fallback...");
      compileSource({ source_code: sourceCode, get_llm_advice: true, stdin_input: stdinInput })
        .then((result) => {
          setCompileResult(result);
          setStatus({ running: false, phase: "done" });
        })
        .catch((error) => {
          setErrorMessage(error.message);
          setStatus(initialStatus);
        });
    };

    ws.onclose = () => {
      if (!finished && status.running) {
        setStatus({ running: false, phase: "done" });
      }
    };
  }

  async function handleSaveSnippet() {
    try {
      const saved = await saveSnippet({ title: `Snippet ${new Date().toISOString()}`, code: sourceCode });
      setErrorMessage(`Snippet saved with ID ${saved.snippet_id}`);
    } catch (error) {
      setErrorMessage(error.message);
    }
  }

  return (
    <main className="min-h-screen bg-ink text-textMain">
      <div className="mx-auto grid max-w-[1600px] grid-rows-[auto,1fr,auto] gap-3 p-3">
        <header className="rounded-xl border border-white/5 bg-surface px-4 py-3 shadow-pane">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <div className="flex items-center gap-3">
              <h1 className="text-lg font-bold tracking-tight">HingC</h1>
              <span className="rounded-full border border-accent/40 bg-accent/15 px-2 py-0.5 text-xs text-accent">AI-Assisted Compiler IDE</span>
            </div>
            <div className="flex items-center gap-2">
              <button
                onClick={() => setDrawerOpen(true)}
                className="rounded-md border border-white/10 bg-panel px-3 py-1 text-xs text-textMain hover:border-accent/40 transition"
              >
                📚 Examples & Docs
              </button>
              <button
                onClick={handleSaveSnippet}
                className="rounded-md border border-white/10 bg-panel px-3 py-1 text-xs text-textMain hover:border-accent/40"
              >
                Save
              </button>
              <button
                onClick={runCompilation}
                className={`rounded-md px-3 py-1 text-xs font-semibold text-black ${
                  status.running ? "bg-accent animate-pulseAccent" : "bg-accent"
                }`}
              >
                Run
              </button>
            </div>
          </div>
          {errorMessage && <p className="mt-2 text-xs text-warning">{errorMessage}</p>}
        </header>

        <section className="grid min-h-[72vh] gap-3 grid-cols-[1.2fr,1fr]">
          <Editor 
            ref={editorRef}
            value={sourceCode} 
            onChange={setSourceCode} 
            onRun={runCompilation} 
            markers={markers} 
          />

          <div className="grid grid-rows-[1fr,auto,auto] gap-3">
            <OutputPanel
              activeTab={activeTab}
              onTabChange={setActiveTab}
              compileResult={compileResult}
              stdinInput={stdinInput}
              onStdinChange={setStdinInput}
            />
            <ErrorPanel
              errors={compileResult?.errors || []}
              warnings={compileResult?.warnings || []}
              sourceCode={sourceCode}
              onJumpToLine={(lineNumber) => editorRef.current?.jumpToLine(lineNumber)}
            />
            <AiAdvisor advice={compileResult?.llm_advice} loading={loadingAdvice} />
          </div>
        </section>

        <footer className="rounded-xl border border-white/5 bg-surface px-3 py-2 text-xs text-muted shadow-pane">
          <div className="flex flex-wrap items-center justify-between gap-2">
            <span>Status: {status.phase}</span>
            <span>
              Errors: {compileResult?.errors?.length || 0} | Warnings: {compileResult?.warnings?.length || 0}
            </span>
          </div>
        </footer>
      </div>

      <ExamplesDocDrawer
        isOpen={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        onSelectExample={setSourceCode}
      />
    </main>
  );
}
