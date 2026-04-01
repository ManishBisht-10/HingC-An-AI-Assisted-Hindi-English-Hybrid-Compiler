import { useState } from "react";
import { copyToClipboard } from "../lib/ui";

export default function AiAdvisor({ advice, loading }) {
  const [expandedId, setExpandedId] = useState(null);
  const [copiedId, setCopiedId] = useState(null);

  const handleCopyFix = (code, errorId) => {
    copyToClipboard(code);
    setCopiedId(errorId);
    setTimeout(() => setCopiedId(null), 2000);
  };

  return (
    <section className="rounded-xl border border-white/5 bg-panel p-3 shadow-pane">
      <div className="mb-3 flex items-center justify-between">
        <h3 className="text-xs uppercase tracking-wide text-muted flex items-center gap-2">
          <span>🤖</span>
          <span>AI Advisor</span>
        </h3>
        {loading && (
          <span className="text-[11px] text-accent inline-flex items-center gap-1">
            <span className="inline-block w-1.5 h-1.5 bg-accent rounded-full animate-pulse"></span>
            Analyzing...
          </span>
        )}
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
                  <span className="text-xs text-muted/40 whitespace-nowrap">
                    {item.fixed_code_snippet && "→ Fix"}
                  </span>
                </div>
              </button>

              {expandedId === item.error_id && (
                <div className="mt-1 ml-2 border-l-2 border-accent/30 pl-2 space-y-1.5 animate-in fade-in duration-200">
                  <div className="text-xs text-textMain leading-relaxed">
                    <p className="mb-1.5"><strong>📝 Issue:</strong></p>
                    <p className="text-white/70">{item.explanation}</p>
                  </div>

                  <div className="text-xs">
                    <p className="mb-1"><strong className="text-success">✓ Fix:</strong></p>
                    <p className="text-white/70">{item.fix_suggestion}</p>
                  </div>

                  {item.fixed_code_snippet && (
                    <div className="mt-2">
                      <div className="flex items-center justify-between mb-1">
                        <span className="text-[10px] text-muted uppercase tracking-wider">
                          Fixed Code
                        </span>
                        <button
                          onClick={() =>
                            handleCopyFix(item.fixed_code_snippet, item.error_id)
                          }
                          className="text-[10px] px-1.5 py-0.5 rounded bg-accentAlt text-black hover:bg-accentAlt/80 transition"
                        >
                          {copiedId === item.error_id
                            ? "✓ Copied"
                            : "Copy"}
                        </button>
                      </div>
                      <pre className="overflow-x-auto rounded bg-surface p-1.5 text-[11px] text-success font-editor border border-white/5">
                        {item.fixed_code_snippet}
                      </pre>
                    </div>
                  )}
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
        </div>
      )}
    </section>
  );
}
