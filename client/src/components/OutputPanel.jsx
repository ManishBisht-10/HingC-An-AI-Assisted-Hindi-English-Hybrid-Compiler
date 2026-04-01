import MonacoEditor from "@monaco-editor/react";
import { useState } from "react";
import AstViewer from "./AstViewer";
import { getTokenColor, copyToClipboard, downloadFile } from "../lib/ui";

const TABS = ["Output", "Generated C", "Tokens", "AST"];

export default function OutputPanel({
  activeTab,
  onTabChange,
  compileResult,
  stdinInput,
  onStdinChange,
}) {
  const execution = compileResult?.execution;
  const tokens = compileResult?.tokens || [];
  const generatedC = compileResult?.generated_c_code || "";
  const [copySuccess, setCopySuccess] = useState(false);

  const handleCopyC = () => {
    copyToClipboard(generatedC);
    setCopySuccess(true);
    setTimeout(() => setCopySuccess(false), 2000);
  };

  const handleDownloadC = () => {
    downloadFile(generatedC, "output.c");
  };

  return (
    <section className="panel-shell h-full rounded-xl border border-white/5 bg-panel shadow-pane">
      <header className="border-b border-white/5 px-3 py-2">
        <div className="flex flex-wrap items-center gap-2">
          {TABS.map((tab) => (
            <button
              key={tab}
              className={`rounded-md px-2 py-1 text-xs transition ${
                activeTab === tab
                  ? "bg-accent text-black"
                  : "bg-surface text-muted hover:text-textMain"
              }`}
              onClick={() => onTabChange(tab)}
            >
              {tab}
            </button>
          ))}
        </div>
      </header>

      <div className="h-[calc(100%-49px)] p-3">
        {activeTab === "Output" && (
          <div className="grid h-full gap-3 md:grid-rows-[auto,1fr]">
            <label className="text-xs text-muted">
              stdin input
              <textarea
                className="mt-1 w-full rounded-md border border-white/10 bg-surface p-2 text-xs text-textMain"
                rows={3}
                value={stdinInput}
                onChange={(event) => onStdinChange(event.target.value)}
                placeholder="Optional input for lo(...)"
              />
            </label>
            <div className="overflow-auto rounded-md border border-white/10 bg-ink p-3 font-editor text-xs">
              <div className="mb-2 text-success whitespace-pre-wrap">{execution?.stdout || ""}</div>
              <div className="text-error whitespace-pre-wrap">{execution?.stderr || ""}</div>
              <div className="mt-4 text-muted">
                {(execution && `Execution time: ${execution.execution_time_ms.toFixed(2)} ms`) ||
                  "Run code to see output"}
              </div>
            </div>
          </div>
        )}

        {activeTab === "Generated C" && (
          <div className="flex h-full flex-col gap-2">
            <div className="flex items-center gap-2">
              <button
                onClick={handleCopyC}
                className="rounded px-2 py-1 text-xs font-medium transition bg-accentAlt text-black hover:bg-accentAlt/80 disabled:opacity-50"
              >
                {copySuccess ? "✓ Copied" : "Copy"}
              </button>
              <button
                onClick={handleDownloadC}
                className="rounded px-2 py-1 text-xs font-medium transition bg-success text-black hover:bg-success/80"
              >
                ⬇ Download
              </button>
              <span className="text-xs text-muted ml-auto">
                {generatedC.split("\n").length} lines
              </span>
            </div>
            <MonacoEditor
              height="100%"
              language="c"
              value={generatedC || "// C output will appear here"}
              options={{
                readOnly: true,
                minimap: { enabled: false },
                automaticLayout: true,
              }}
              theme="vs-dark"
            />
          </div>
        )}

        {activeTab === "Tokens" && (
          <div className="h-full overflow-auto rounded-md border border-white/10 bg-ink">
            <table className="w-full text-left text-xs">
              <thead className="sticky top-0 bg-surface text-muted">
                <tr>
                  <th className="px-3 py-2">Type</th>
                  <th className="px-3 py-2">Value</th>
                  <th className="px-3 py-2">Line</th>
                  <th className="px-3 py-2">Column</th>
                </tr>
              </thead>
              <tbody>
                {tokens.map((token, index) => (
                  <tr
                    key={`${token.type}-${index}`}
                    className="border-t border-white/5 hover:bg-surface/50 transition"
                  >
                    <td
                      className={`px-3 py-2 font-semibold ${getTokenColor(
                        token.type
                      )}`}
                    >
                      {token.type}
                    </td>
                    <td className="px-3 py-2 font-editor">{token.value}</td>
                    <td className="px-3 py-2 text-muted">{token.line}</td>
                    <td className="px-3 py-2 text-muted">{token.column}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}

        {activeTab === "AST" && (
          <div className="h-full overflow-auto rounded-md border border-white/10 bg-ink p-3">
            <AstViewer ast={compileResult?.ast_json} />
          </div>
        )}
      </div>
    </section>
  );
}
