const TOKEN_COLORS = {
  keyword: "text-accent",
  type: "text-accentAlt",
  constant: "text-success",
  comment: "text-muted",
  string: "text-warning",
  number: "text-accentAlt",
  operator: "text-textMain",
  delimiter: "text-textMain",
  identifier: "text-textMain",
};

export function getTokenColor(tokenType) {
  return TOKEN_COLORS[tokenType] || "text-textMain";
}

export function copyToClipboard(text) {
  navigator.clipboard.writeText(text).catch(() => {
    // Fallback for older browsers
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  });
}

export function downloadFile(content, filename) {
  const blob = new Blob([content], { type: "text/plain" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
