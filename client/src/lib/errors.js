export function groupErrorsByPhase(errors) {
  const grouped = {};
  errors.forEach((error) => {
    const phase = error.phase || "compiler";
    if (!grouped[phase]) {
      grouped[phase] = [];
    }
    grouped[phase].push(error);
  });
  return grouped;
}

export function getSeverityInfo(type) {
  const severityMap = {
    syntax: { label: "Syntax", color: "text-error", bg: "bg-error/10", border: "border-error/50" },
    semantic: {
      label: "Semantic",
      color: "text-error",
      bg: "bg-error/10",
      border: "border-error/50",
    },
    type: { label: "Type", color: "text-error", bg: "bg-error/10", border: "border-error/50" },
    warning: { label: "Warning", color: "text-warning", bg: "bg-warning/10", border: "border-warning/40" },
  };
  return severityMap[type] || severityMap.semantic;
}

export function getPhaseIcon(phase) {
  const icons = {
    lexer: "🔤",
    parser: "🌳",
    semantic: "✓",
    codegen: "⚙️",
  };
  return icons[phase?.toLowerCase()] || "⚠️";
}
