import Editor from "@monaco-editor/react";

interface Props {
  value: string;
  onChange: (value: string) => void;
}

export function DocEditor({ value, onChange }: Props) {
  return (
    <div className="h-[70vh] border border-[#1a1a1a] rounded-xl overflow-hidden shadow-2xl bg-[#1e1e1e]">
      <Editor
        height="100%"
        defaultLanguage="markdown"
        theme="vs-dark"
        value={value}
        onChange={(v) => onChange(v ?? "")}
        options={{ 
          minimap: { enabled: false }, 
          wordWrap: "on", 
          lineNumbers: "on",
          fontSize: 14,
          fontFamily: "JetBrains Mono, Fira Code, Monaco, Courier New, monospace",
          cursorBlinking: "smooth",
          padding: { top: 12, bottom: 12 }
        }}
      />
    </div>
  );
}
