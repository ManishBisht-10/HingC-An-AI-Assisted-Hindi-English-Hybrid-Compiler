import { useState } from "react";
import { EXAMPLES, LANGUAGE_DOCS } from "../lib/examples";

function Drawer({ isOpen, onClose, title, children }) {
  return (
    <>
      {isOpen && (
        <div className="fixed inset-0 bg-black/50 z-40" onClick={onClose} />
      )}
      <div
        className={`fixed right-0 top-0 h-screen w-96 bg-panel border-l border-white/5 shadow-pane transform transition-transform duration-300 z-50 overflow-y-auto ${
          isOpen ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div className="sticky top-0 border-b border-white/5 bg-surface p-4 flex items-center justify-between">
          <h2 className="font-semibold text-textMain">{title}</h2>
          <button
            onClick={onClose}
            className="text-muted hover:text-textMain transition text-lg"
          >
            ✕
          </button>
        </div>
        <div className="p-4">{children}</div>
      </div>
    </>
  );
}

export default function ExamplesDocDrawer({ isOpen, onClose, onSelectExample }) {
  const [activeTab, setActiveTab] = useState("examples");

  return (
    <Drawer isOpen={isOpen} onClose={onClose} title="Examples & Docs">
      <div className="space-y-3">
        <div className="flex gap-2 border-b border-white/10">
          <button
            onClick={() => setActiveTab("examples")}
            className={`pb-2 text-xs font-semibold transition ${
              activeTab === "examples"
                ? "text-accent border-b-2 border-accent"
                : "text-muted hover:text-textMain"
            }`}
          >
            Examples
          </button>
          <button
            onClick={() => setActiveTab("docs")}
            className={`pb-2 text-xs font-semibold transition ${
              activeTab === "docs"
                ? "text-accent border-b-2 border-accent"
                : "text-muted hover:text-textMain"
            }`}
          >
            Language Ref
          </button>
        </div>

        {activeTab === "examples" && (
          <div className="space-y-2">
            {EXAMPLES.map((example) => (
              <button
                key={example.id}
                onClick={() => {
                  onSelectExample(example.code);
                  onClose();
                }}
                className="w-full text-left p-2 rounded-md border border-white/10 bg-ink hover:border-accent/40 hover:bg-accent/5 transition"
              >
                <div className="text-xs font-semibold text-accent">
                  {example.title}
                </div>
                <div className="text-[11px] text-muted mt-0.5">
                  {example.description}
                </div>
              </button>
            ))}
          </div>
        )}

        {activeTab === "docs" && (
          <div className="space-y-4">
            <section>
              <h3 className="text-xs font-semibold text-accent mb-2">
                Keywords
              </h3>
              <div className="space-y-1.5 max-h-64 overflow-y-auto">
                {LANGUAGE_DOCS.keywords.map((item, idx) => (
                  <div
                    key={idx}
                    className="text-[11px] bg-ink p-1.5 rounded border border-white/5"
                  >
                    <div className="font-mono text-success">{item.kw}</div>
                    <div className="text-muted">{item.meaning}</div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xs font-semibold text-accent mb-2">
                Operators
              </h3>
              <div className="space-y-1.5 max-h-48 overflow-y-auto">
                {LANGUAGE_DOCS.operators.map((item, idx) => (
                  <div
                    key={idx}
                    className="text-[11px] bg-ink p-1.5 rounded border border-white/5"
                  >
                    <div className="font-mono text-warning">{item.op}</div>
                    <div className="text-muted">{item.meaning}</div>
                  </div>
                ))}
              </div>
            </section>

            <section>
              <h3 className="text-xs font-semibold text-accent mb-2">Tips</h3>
              <div className="space-y-1">
                {LANGUAGE_DOCS.tips.map((tip, idx) => (
                  <div
                    key={idx}
                    className="text-[11px] text-muted leading-relaxed p-1.5 bg-ink rounded border border-white/5"
                  >
                    💡 {tip}
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </Drawer>
  );
}
