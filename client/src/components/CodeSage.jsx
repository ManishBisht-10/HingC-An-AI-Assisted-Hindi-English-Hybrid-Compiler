import { useState } from "react";

export default function CodeSage({ advice, loading }) {
  const [expandedId, setExpandedId] = useState(null);

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
                    <p className="mb-1.5"><strong>📝 Issue:</strong></p>
                    <p className="text-white/70">{item.explanation}</p>
                  </div>

                  <div className="text-xs">
                    <p className="mb-1"><strong className="text-success">✓ Detailed Advice:</strong></p>
                    <p className="text-white/70">{item.fix_suggestion}</p>
                  </div>
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
    </section>
  );
}