export default function ExamplesDropdown({ examples, onSelect, loading }) {
  return (
    <select
      className="rounded-md border border-white/10 bg-panel px-2 py-1 text-xs text-textMain"
      onChange={(event) => {
        const value = event.target.value;
        if (!value) {
          return;
        }
        const selected = examples.find((item) => item.name === value);
        if (selected) {
          onSelect(selected.code);
        }
      }}
      defaultValue=""
      disabled={loading}
    >
      <option value="">Examples</option>
      {examples.map((example) => (
        <option key={example.name} value={example.name}>
          {example.name}
        </option>
      ))}
    </select>
  );
}
