import { useState } from "react";

function AstNode({ node, nodeKey, depth = 0 }) {
  const [expanded, setExpanded] = useState(depth < 2);

  if (node === null || node === undefined) {
    return <div className="text-muted">null</div>;
  }

  if (typeof node !== "object") {
    return <span className="text-success">{JSON.stringify(node)}</span>;
  }

  if (Array.isArray(node)) {
    if (node.length === 0) {
      return <span className="text-muted">[]</span>;
    }
    return (
      <div>
        <button
          className="text-accent hover:underline"
          onClick={() => setExpanded(!expanded)}
        >
          {expanded ? "▼" : "▶"} Array[{node.length}]
        </button>
        {expanded && (
          <div className="ml-4 border-l border-white/10 pl-2">
            {node.map((item, idx) => (
              <div key={idx}>
                <span className="text-muted">[{idx}]:</span>
                <AstNode node={item} nodeKey={idx} depth={depth + 1} />
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  const keys = Object.keys(node);
  if (keys.length === 0) {
    return <span className="text-muted">{"{}"}</span>;
  }

  return (
    <div>
      <button
        className="text-accent hover:underline"
        onClick={() => setExpanded(!expanded)}
      >
        {expanded ? "▼" : "▶"} {nodeKey || "Object"}
      </button>
      {expanded && (
        <div className="ml-4 border-l border-white/10 pl-2">
          {keys.map((key) => (
            <div key={key} className="my-1">
              <span className="text-textMain">{key}:</span>
              <AstNode node={node[key]} nodeKey={key} depth={depth + 1} />
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function AstViewer({ ast }) {
  if (!ast) {
    return <div className="text-muted">No AST available</div>;
  }

  return (
    <div className="font-editor text-xs text-white/80 space-y-1">
      <AstNode node={ast} nodeKey="Program" depth={0} />
    </div>
  );
}
