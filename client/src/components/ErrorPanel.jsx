import { groupErrorsByPhase, getSeverityInfo, getPhaseIcon } from "../lib/errors";

export default function ErrorPanel({ errors = [], warnings = [], sourceCode = "", onJumpToLine }) {
  const hasIssues = errors.length > 0 || warnings.length > 0;
  const groupedErrors = groupErrorsByPhase(errors);

  const getLineContent = (lineNum) => {
    if (!sourceCode) return "";
    const lines = sourceCode.split("\n");
    return lines[lineNum - 1] || "";
  };

  if (!hasIssues) {
    return (
      <section className="rounded-xl border border-white/5 bg-panel p-3 text-xs text-muted shadow-pane">
        <div className="flex items-center gap-2">
          <span>✓</span>
          <span>No compiler issues</span>
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-white/5 bg-panel p-3 shadow-pane">
      <div className="mb-3 flex items-center justify-between">
        <div className="text-xs uppercase tracking-wide text-muted">Diagnostics</div>
        <div className="flex gap-3 text-xs text-muted">
          <span>
            <span className="text-error font-semibold">{errors.length}</span> Error{errors.length !== 1 ? "s" : ""}
          </span>
          {warnings.length > 0 && (
            <span>
              <span className="text-warning font-semibold">{warnings.length}</span> Warning{warnings.length !== 1 ? "s" : ""}
            </span>
          )}
        </div>
      </div>

      <div className="max-h-56 overflow-y-auto space-y-2">
        {Object.entries(groupedErrors).map(([phase, phaseErrors]) => (
          <div key={phase}>
            <div className="mb-1.5 text-xs font-semibold text-muted/70 flex items-center gap-2">
              <span>{getPhaseIcon(phase)}</span>
              <span>{phase.toUpperCase()}</span>
              <span className="text-xs bg-surface px-1.5 py-0.5 rounded">
                {phaseErrors.length}
              </span>
            </div>
            <div className="space-y-1.5 ml-3">
              {phaseErrors.map((error, idx) => {
                const severity = getSeverityInfo(error.type || "semantic");
                const lineContent = getLineContent(error.line);
                return (
                  <button
                    type="button"
                    key={`error-${phase}-${idx}`}
                    onClick={() => onJumpToLine?.(error.line || 1)}
                    className={`w-full rounded-md border transition p-2 text-left hover:border-accent/60 hover:bg-accent/5 ${severity.border} ${severity.bg}`}
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1">
                        <div className={`text-[11px] font-semibold ${severity.color}`}>
                          Line {error.line || "?"}
                          {error.column && `:${error.column}`}
                        </div>
                        <div className="mt-1 text-xs text-textMain leading-snug">
                          {error.message}
                        </div>
                        {lineContent && (
                          <div className="mt-1.5 text-[10px] font-editor text-muted/60 bg-ink/50 rounded px-1.5 py-0.5 truncate">
                            {lineContent.trim()}
                          </div>
                        )}
                      </div>
                      <div className="text-xs text-muted/40 whitespace-nowrap pt-1">→</div>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        ))}

        {warnings.length > 0 && (
          <div>
            <div className="mb-1.5 text-xs font-semibold text-muted/70 flex items-center gap-2">
              <span>⚠️</span>
              <span>WARNINGS</span>
              <span className="text-xs bg-surface px-1.5 py-0.5 rounded">
                {warnings.length}
              </span>
            </div>
            <div className="space-y-1.5 ml-3">
              {warnings.map((warning, idx) => (
                <div
                  key={`warning-${idx}`}
                  className="rounded-md border border-warning/40 bg-warning/10 p-2 text-xs text-textMain"
                >
                  {typeof warning === "string" ? warning : warning.message || JSON.stringify(warning)}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </section>
  );
}
