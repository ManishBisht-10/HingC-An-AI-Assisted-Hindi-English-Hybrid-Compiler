import { useState } from "react";
import { DiffEditor } from "@monaco-editor/react";
import { HINGC_LANGUAGE_ID } from "../lib/hingcLanguage";

export default function CodeSage({ advice, loading, onRun, compileResult, onJumpToLine, onApplyFix, showMarkers = true, onToggleMarkers, sourceCode = "", llmLanguage = "hinglish", onLanguageChange, onUndo }) {
  const [expandedId, setExpandedId] = useState(null);
  const [showExecution, setShowExecution] = useState(true);
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewText, setPreviewText] = useState("");

  function makePreviewSegments(originalSource, fixedSnippet, lineNumber) {
    const lines = originalSource.split("\n");
    const idx = Math.max(0, Math.min(lines.length - 1, (lineNumber || 1) - 1));
    const fixedLines = fixedSnippet.split("\n");
    const newLines = [...lines.slice(0, idx), ...fixedLines, ...lines.slice(idx + 1)];

    const contextBefore = Math.max(0, idx - 3);
    const contextAfter = Math.min(newLines.length, idx + fixedLines.length + 3);

    const originalSegment = lines.slice(contextBefore, contextAfter).join('\n');
    const newSegment = newLines.slice(contextBefore, contextAfter).join('\n');
    return { originalSegment, newSegment, fixedSnippet, line: lineNumber };
  }

  function copyToClipboard(text) {
    try {
      navigator.clipboard.writeText(text);
    } catch (e) {
      // ignore
    }
  }

  return (
    <section className="rounded-xl border border-white/5 bg-panel p-3 shadow-pane">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-xs uppercase tracking-wide text-muted flex items-center gap-2">
          <span>🤖</span>
          <span>CodeSage</span>
        </h3>
        {loading && (
          <span className="text-[11px] text-accent inline-flex items-center gap-1">
            <span className="inline-block w-1.5 h-1.5 bg-accent rounded-full animate-pulse"></span>
            Analyzing...
          </span>
        )}
            {previewOpen && (
              <div className="fixed inset-0 z-50 flex items-center justify-center">
                <div className="absolute inset-0 bg-black/50" onClick={() => setPreviewOpen(false)} />
                <div className="relative max-w-5xl w-full rounded bg-surface p-4">
                  <div className="flex items-center justify-between">
                    <h4 className="text-sm font-semibold">Preview Suggested Change</h4>
                    <div className="flex items-center gap-2">
                      <button onClick={() => copyToClipboard(previewText.fixedSnippet || previewText.newSegment || "")} className="text-xs px-2 py-1 bg-panel rounded">Copy</button>
                      <button onClick={() => setPreviewOpen(false)} className="text-xs px-2 py-1">Close</button>
                    </div>
                  </div>
                  <div className="mt-2">
                    <DiffEditor
                      height="60vh"
                      original={previewText.originalSegment || ""}
                      modified={previewText.newSegment || ""}
                      language={HINGC_LANGUAGE_ID}
                      options={{ readOnly: true, renderSideBySide: true, automaticLayout: true }}
                    />
                  </div>
                  <div className="mt-3 flex justify-end gap-2">
                    <button
                      onClick={() => {
                        if (onApplyFix && (previewText.fixedSnippet || previewText.newSegment)) {
                          onApplyFix(previewText.fixedSnippet || previewText.newSegment, previewText.line);
                        }
                        setPreviewOpen(false);
                      }}
                      className="rounded-md bg-accent px-3 py-1 text-sm text-black"
                    >
                      Apply From Preview
                    </button>
                    <button onClick={() => setPreviewOpen(false)} className="rounded-md px-3 py-1 text-sm border">Close</button>
                  </div>
                </div>
              </div>
            )}
        <div className="flex items-center gap-2">
          <button
            onClick={() => onRun && onRun()}
            className="rounded-md px-2 py-1 text-xs font-semibold bg-accent text-black"
          >
            Compile
          </button>
          <div className="flex items-center gap-2">
            <label className="text-xs text-muted flex items-center gap-2">
              <span className="text-[12px]">LLM:</span>
              <select value={llmLanguage} onChange={(e) => onLanguageChange && onLanguageChange(e.target.value)} className="text-xs bg-panel rounded px-2 py-0.5">
                <option value="hinglish">Hinglish</option>
                <option value="english">English</option>
              </select>
            </label>
            <button onClick={() => onUndo && onUndo()} className="rounded-md px-2 py-1 text-xs bg-ink border border-white/10">Undo Fix</button>
          </div>
        </div>
      </div>

      {!advice && !loading && (
        <p className="text-xs text-muted">Run compiler to get AI-powered explanations and fix suggestions.</p>
      )}

      {advice && (
        <div className="max-h-56 space-y-2 overflow-auto">
          {(advice.error_explanations || []).map((item) => (
            <div key={item.error_id}>
              <button
                onClick={() =>
                  setExpandedId(expandedId === item.error_id ? null : item.error_id)
                }
                className="w-full rounded-md border border-white/10 bg-ink p-2 text-left hover:border-accent/40 transition"
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 text-xs">
                    <div className="font-semibold text-accent">
                      {expandedId === item.error_id ? "▼" : "▶"} {item.error_id}
                    </div>
                    {expandedId !== item.error_id && (
                      <p className="mt-1 text-white/60 line-clamp-1">
                        {item.explanation}
                      </p>
                    )}
                  </div>
                  <span className="text-xs text-muted/40 whitespace-nowrap">→ Advice</span>
                </div>
              </button>

              {expandedId === item.error_id && (
                <div className="mt-1 ml-2 border-l-2 border-accent/30 pl-2 space-y-1.5 animate-in fade-in duration-200">
                  <div className="text-xs text-textMain leading-relaxed">
                    <p className="mb-1.5"><strong>📝 Root cause:</strong></p>
                    <p className="text-white/70">{item.explanation}</p>
                    <p className="mt-1 text-[12px] text-muted">Confidence: {(item.confidence || 0).toFixed ? (item.confidence * 100).toFixed(0) + '%' : String(item.confidence)}</p>
                  </div>

                  <div className="text-xs">
                    <p className="mb-1"><strong className="text-success">✓ One-line fix:</strong></p>
                    <p className="text-white/70">{item.fix_suggestion}</p>
                  </div>

                  {item.candidates && item.candidates.length > 0 ? (
                    <div className="mt-2">
                      <p className="mb-1 text-xs font-semibold">Candidate fixes</p>
                      <ul className="space-y-1">
                        {item.candidates.map((c, ci) => (
                          <li key={ci} className="flex items-start justify-between gap-2">
                            <div className="text-[12px]">
                              <div className="text-white/70 mb-1">{c.fix_snippet}</div>
                              <div className="text-xs text-muted">Confidence: {Math.round((c.confidence || 0) * 100)}%</div>
                            </div>
                            <div className="flex flex-col gap-1">
                              <button
                                onClick={() => onApplyFix && onApplyFix(c.fix_snippet, item.line)}
                                className="rounded-sm px-2 py-1 text-[12px] bg-panel border border-white/10 ml-2"
                              >
                                Apply
                              </button>
                              <button
                                onClick={() => {
                                  try {
                                    const preview = makePreviewSegments(sourceCode || '', c.fix_snippet, item.line);
                                    setPreviewText(preview);
                                    setPreviewOpen(true);
                                  } catch (e) {
                                    setPreviewText({ originalSegment: 'Preview failed', newSegment: 'Preview failed', fixedSnippet: 'Preview failed', line: null });
                                    setPreviewOpen(true);
                                  }
                                }}
                                className="rounded-sm px-2 py-1 text-[12px] bg-ink border border-white/10 ml-2"
                              >
                                Preview
                              </button>
                            </div>
                          </li>
                        ))}
                      </ul>
                    </div>
                  ) : item.fixed_code_snippet ? (
                    <div className="mt-2">
                      <p className="mb-1 text-xs font-semibold">Suggested fix snippet</p>
                      <pre className="bg-black/20 p-2 text-[12px] rounded max-h-36 overflow-auto">{item.fixed_code_snippet}</pre>
                    </div>
                  ) : null}
                </div>
              )}
            </div>
          ))}

          {advice.overall_summary && (
            <div className="rounded-md border border-accent/40 bg-accent/10 p-2 text-xs text-textMain">
              <div className="flex items-start gap-2">
                <span className="text-accent">💡</span>
                <p>{advice.overall_summary}</p>
              </div>
            </div>
          )}

          {(advice.code_quality_tips || []).length > 0 && (
            <div className="rounded-md border border-white/10 bg-ink p-2 text-xs text-textMain">
              <p className="mb-1 font-semibold text-muted">CodeSage Tips</p>
              <ul className="space-y-1 text-white/70">
                {(advice.code_quality_tips || []).map((tip, idx) => (
                  <li key={idx}>- {tip}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
      <div className="mt-2 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <label className="text-xs text-muted flex items-center gap-2">
            <input type="checkbox" checked={showMarkers} onChange={() => onToggleMarkers && onToggleMarkers()} />
            <span>Show markers</span>
          </label>
        </div>
      </div>
      {/* Execution & errors panel */}
      {compileResult && (
        <div className="mt-3 rounded-md border border-white/10 bg-ink p-2 text-xs text-textMain">
          <div className="flex items-center justify-between">
            <div className="font-semibold">Last Run</div>
            <div className="text-xs text-muted">Success: {String(compileResult.success)}</div>
          </div>

          {compileResult.execution && (
            <div className="mt-2">
              <div className="text-xs font-semibold">Execution Output</div>
              <pre className="mt-1 max-h-24 overflow-auto text-[12px] bg-black/20 p-2 rounded">{compileResult.execution.stdout || ""}</pre>
              {compileResult.execution.stderr && (
                <pre className="mt-1 max-h-24 overflow-auto text-[12px] bg-black/20 p-2 rounded text-warning">{compileResult.execution.stderr}</pre>
              )}
            </div>
          )}

          {(compileResult.errors || []).length > 0 && (
            <div className="mt-2">
              <div className="text-xs font-semibold">Errors</div>
              <ul className="mt-1 space-y-1 text-white/70">
                {compileResult.errors.map((err, idx) => (
                  <li key={`${err.phase}-${err.line}-${err.column}-${idx}`}>
                    <div className="flex items-center justify-between gap-2">
                      <button
                        onClick={() => onJumpToLine && onJumpToLine(err.line)}
                        className="text-left text-[13px] underline"
                      >
                        Line {err.line}:{err.column} — {err.message}
                      </button>
                      {/* If advice exists for this error, show Apply Fix */}
                      {advice && (() => {
                        try {
                          const id = `E${idx + 1}`;
                          const item = (advice.error_explanations || []).find((x) => x.error_id === id);
                          if (item && item.fixed_code_snippet) {
                            return (
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => {
                                    if (onApplyFix) onApplyFix(item.fixed_code_snippet, err.line);
                                  }}
                                  className="rounded-sm px-2 py-1 text-[12px] bg-panel border border-white/10 ml-2"
                                >
                                  Apply Fix
                                </button>
                                <button
                                  onClick={() => {
                                    try {
                                      const preview = makePreviewSegments(sourceCode || '', item.fixed_code_snippet, err.line);
                                      setPreviewText(preview);
                                      setPreviewOpen(true);
                                    } catch (e) {
                                      setPreviewText({ originalSegment: 'Preview failed', newSegment: 'Preview failed', fixedSnippet: 'Preview failed', line: null });
                                      setPreviewOpen(true);
                                    }
                                  }}
                                  className="rounded-sm px-2 py-1 text-[12px] bg-ink border border-white/10 ml-2"
                                >
                                  Preview
                                </button>
                              </div>
                            );
                          }
                        } catch (e) {
                          /* ignore */
                        }
                        return null;
                      })()}
                    </div>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      )}
    </section>
  );
}