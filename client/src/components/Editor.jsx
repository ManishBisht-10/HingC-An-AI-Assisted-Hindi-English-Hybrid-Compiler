import { useEffect, useRef, forwardRef, useImperativeHandle } from "react";
import MonacoEditor from "@monaco-editor/react";
import { HINGC_LANGUAGE_ID, registerHingcLanguage } from "../lib/hingcLanguage";

const MONACO_THEME = "hingc-dark";

function defineTheme(monaco) {
  monaco.editor.defineTheme(MONACO_THEME, {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "comment", foreground: "888888" },
      { token: "string", foreground: "f9b36b" },
      { token: "keyword", foreground: "5da8ff" },
      { token: "type", foreground: "59d185" },
      { token: "number", foreground: "ffaa66" },
      { token: "constant", foreground: "ffaa66" },
      { token: "operator", foreground: "E8E8E8" },
      { token: "identifier", foreground: "E8E8E8" },
    ],
    colors: {
      "editor.background": "#0D0D0D",
      "editorLineNumber.foreground": "#4B4B4B",
      "editorCursor.foreground": "#FF6B2B",
      "editor.selectionBackground": "#2B2B2B",
      "editor.inactiveSelectionBackground": "#222222",
    },
  });
}

export default forwardRef(function Editor({ value, onChange, onRun, markers = [] }, ref) {
  const editorRef = useRef(null);
  const monacoRef = useRef(null);

  useImperativeHandle(ref, () => ({
    jumpToLine: (lineNumber) => {
      if (editorRef.current) {
        editorRef.current.revealLineInCenter(lineNumber);
        editorRef.current.setPosition({ lineNumber, column: 1 });
      }
    },
    applyFix: (fixedCode, lineNumber) => {
      try {
        const editor = editorRef.current;
        if (!editor) return;
        const model = editor.getModel();
        if (!model) return;
        const full = model.getValue();
        const lines = full.split(/\r?\n/);
        if (lineNumber && lineNumber >= 1 && lineNumber <= lines.length) {
          // Replace the specified line (1-based) with the fixed code
          lines[lineNumber - 1] = fixedCode;
        } else {
          // If no valid line provided, append the fix at the end
          lines.push(fixedCode);
        }
        const updated = lines.join("\n");
        model.setValue(updated);
        // move cursor to the fixed line
        if (lineNumber) {
          editor.revealLineInCenter(lineNumber);
          editor.setPosition({ lineNumber, column: 1 });
        }
      } catch (e) {
        // ignore errors
      }
    },
    undo: () => {
      try {
        const editor = editorRef.current;
        if (!editor) return;
        // Trigger Monaco undo command
        editor.trigger('hingc', 'undo', null);
      } catch (e) {
        // ignore
      }
    },
  }));

  function handleMount(editor, monaco) {
    editorRef.current = editor;
    monacoRef.current = monaco;
    registerHingcLanguage(monaco);
    defineTheme(monaco);
    monaco.editor.setTheme(MONACO_THEME);

    editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.Enter, () => {
      onRun();
    });

    monaco.editor.setModelMarkers(editor.getModel(), "hingc-owner", markers);
  }

  function handleEditorChange(nextValue) {
    onChange(nextValue || "");
  }

  function handleBeforeMount(monaco) {
    registerHingcLanguage(monaco);
    defineTheme(monaco);
  }

  useEffect(() => {
    const monaco = monacoRef.current;
    const model = editorRef.current?.getModel();
    if (monaco && model) {
      monaco.editor.setModelMarkers(model, "hingc-owner", markers);
    }
  }, [markers]);

  return (
    <section className="panel-shell h-full overflow-hidden rounded-xl border border-white/5 bg-panel shadow-pane">
      <header className="flex items-center justify-between border-b border-white/5 px-3 py-2 text-xs text-muted">
        <span className="tracking-wide text-textMain">HingC Editor</span>
        <span>Ctrl+Enter to run</span>
      </header>
      <div className="h-[calc(100%-37px)]">
        <MonacoEditor
          height="100%"
          defaultLanguage={HINGC_LANGUAGE_ID}
          language={HINGC_LANGUAGE_ID}
          value={value}
          beforeMount={handleBeforeMount}
          onMount={handleMount}
          onChange={handleEditorChange}
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            fontFamily: "Fira Code, monospace",
            fontLigatures: true,
            automaticLayout: true,
            scrollBeyondLastLine: false,
            padding: { top: 14 },
          }}
        />
      </div>
    </section>
  );
});
